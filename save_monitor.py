"""
Save File Monitor for Victoria 3
Watches save game directory and processes new saves
"""

import json
import queue
import re
import shutil
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from data_extractor import BinarySaveParseError, ParserRuntimeUnavailableError

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEventHandler = object  # type: ignore[assignment]
    Observer = None


class _SaveFileEventHandler(FileSystemEventHandler):
    """Filesystem event handler for .v3 save files."""

    def __init__(self, monitor: "SaveMonitor"):
        self.monitor = monitor
        super().__init__()

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        self._handle_event(event)

    def on_moved(self, event):
        if event.is_directory:
            return
        self.monitor.enqueue_event(Path(event.dest_path))

    def _handle_event(self, event):
        if event.is_directory:
            return
        self.monitor.enqueue_event(Path(event.src_path))


@dataclass
class _QueuedSaveTask:
    queued_path: Path
    source_path: Path
    signature: Dict[str, int]
    playthrough_id: str
    queued_at_epoch: float


class SaveMonitor:
    """Monitors Victoria 3 save directory for save changes."""

    _EVENT_STOP = object()
    _PROCESS_STOP = object()

    def __init__(self, save_directory: str, data_output_dir: str = "./data"):
        self.save_directory = Path(save_directory)
        self.data_output_dir = Path(data_output_dir)
        self.data_output_dir.mkdir(exist_ok=True)
        self.processed_saves_dir = self.data_output_dir / "processed_saves"
        self.processed_saves_dir.mkdir(exist_ok=True)
        self.queued_saves_dir = self.data_output_dir / "queued_saves"
        self.queued_saves_dir.mkdir(exist_ok=True)

        # In-memory tracking
        self.file_signatures: Dict[str, Dict[str, int]] = {}
        self.seen_game_days: Dict[str, Set[int]] = {}
        self.seen_signature_keys: Set[str] = set()
        self.tracking_data: Dict[str, List] = {}  # playthrough_id -> [data_points]

        # Runtime counters and state persistence lock
        self._stats_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self.run_stats: Dict[str, int] = self._new_run_stats()

        # Runtime state for event-driven monitoring
        self.running = False
        self._debounce_seconds = 1.5
        self._callback: Optional[Callable[[Path, str], Optional[Dict[str, Any]]]] = None
        self._event_queue: "queue.Queue[Union[Path, object]]" = queue.Queue()
        self._process_queue: "queue.Queue[Union[_QueuedSaveTask, object]]" = queue.Queue()
        self._observer = None
        self._capture_thread: Optional[threading.Thread] = None
        self._process_thread: Optional[threading.Thread] = None

        # Load persisted monitor state
        self._load_state()

    @staticmethod
    def _new_run_stats() -> Dict[str, int]:
        return {
            "processed": 0,
            "duplicate_skipped": 0,
            "event_duplicate_skipped": 0,
            "captured": 0,
            "unsupported_format": 0,
            "error": 0,
        }

    def reset_run_stats(self):
        with self._stats_lock:
            self.run_stats = self._new_run_stats()

    def _increment_stat(self, key: str, amount: int = 1):
        with self._stats_lock:
            self.run_stats[key] = self.run_stats.get(key, 0) + amount

    def get_run_stats_snapshot(self) -> Dict[str, int]:
        with self._stats_lock:
            return dict(self.run_stats)

    @staticmethod
    def _safe_qsize(q: queue.Queue) -> int:
        try:
            return int(q.qsize())
        except (NotImplementedError, AttributeError):
            return 0

    def get_queue_backlog_snapshot(self) -> Dict[str, int]:
        """Return queued work counts for status reporting."""
        return {
            "event_queue": self._safe_qsize(self._event_queue),
            "process_queue": self._safe_qsize(self._process_queue),
        }

    def _load_state(self):
        """Load monitor state with migration from legacy path-only format."""
        state_file = self.data_output_dir / "monitor_state.json"
        if not state_file.exists():
            return

        try:
            with open(state_file, "r") as f:
                state = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read monitor state: {e}")
            return

        state_version = state.get("state_version")

        # New formats
        if state_version in (2, 3):
            raw_signatures = state.get("file_signatures", {})
            if isinstance(raw_signatures, dict):
                for path_key, sig in raw_signatures.items():
                    if not isinstance(sig, dict):
                        continue
                    mtime_ns = sig.get("mtime_ns")
                    size = sig.get("size")
                    if isinstance(mtime_ns, int) and isinstance(size, int):
                        self.file_signatures[path_key] = {"mtime_ns": mtime_ns, "size": size}

            raw_seen_days = state.get("seen_game_days", {})
            if isinstance(raw_seen_days, dict):
                for playthrough_id, days in raw_seen_days.items():
                    if not isinstance(days, list):
                        continue
                    normalized_days = set()
                    for day in days:
                        try:
                            normalized_days.add(int(day))
                        except (TypeError, ValueError):
                            continue
                    self.seen_game_days[playthrough_id] = normalized_days

            if state_version == 3:
                raw_signature_keys = state.get("seen_signature_keys", [])
                if isinstance(raw_signature_keys, list):
                    self.seen_signature_keys = set(str(v) for v in raw_signature_keys)

            print(
                f"Loaded state v{state_version}: {len(self.file_signatures)} file signatures, "
                f"{sum(len(v) for v in self.seen_game_days.values())} seen game days"
            )
            return

        # Legacy migration (v1 had processed_files only)
        legacy_paths = state.get("processed_files", [])
        if isinstance(legacy_paths, list) and legacy_paths:
            print("Migrating legacy monitor state to v3 format")
        self.file_signatures = {}
        self.seen_game_days = {}
        self.seen_signature_keys = set()
        self._save_state()

    def _save_state(self):
        """Persist current monitor state."""
        state_file = self.data_output_dir / "monitor_state.json"
        serializable_days = {
            playthrough_id: sorted(list(days))
            for playthrough_id, days in self.seen_game_days.items()
        }
        with self._state_lock:
            with open(state_file, "w") as f:
                json.dump(
                    {
                        "state_version": 3,
                        "file_signatures": self.file_signatures,
                        "seen_game_days": serializable_days,
                        "seen_signature_keys": sorted(list(self.seen_signature_keys)),
                        "last_update": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

    def get_save_files(self) -> List[Path]:
        """Get all .v3 save files in directory."""
        if not self.save_directory.exists():
            print(f"Warning: Save directory not found: {self.save_directory}")
            return []

        return sorted(self.save_directory.glob("*.v3"), key=lambda p: p.stat().st_mtime)

    def identify_playthrough(self, save_file: Path) -> str:
        """Identify which playthrough a save belongs to."""
        name = save_file.stem

        for suffix in ["_autosave", "_backup", "_Autosave", "_Backup", "autosave", "backup"]:
            name = name.replace(suffix, "")

        name = re.sub(r"_\d{4}_\d{1,2}_\d{1,2}", "", name)
        name = re.sub(r"_\d{4}", "", name)
        name = re.sub(r"_\d+$", "", name)
        name = re.sub(r"_+", "_", name).strip("_")

        return name if name else "campaign"

    def _path_key(self, save_file: Path) -> str:
        """Create stable key for state maps."""
        try:
            return str(save_file.resolve())
        except Exception:
            return str(save_file.absolute())

    def _is_watch_target(self, save_file: Path) -> bool:
        """True if this is a top-level .v3 file in the watched directory."""
        if save_file.suffix.lower() != ".v3":
            return False
        try:
            return save_file.parent.resolve() == self.save_directory.resolve()
        except Exception:
            return save_file.parent.absolute() == self.save_directory.absolute()

    @staticmethod
    def _is_autosave_file(save_file: Path) -> bool:
        """Autosave slots are rotated by Victoria 3 and should be archived."""
        return "autosave" in save_file.stem.lower()

    @staticmethod
    def _to_game_day(year: int, month: int, day: int) -> int:
        return (year - 1836) * 365 + (month - 1) * 30 + day

    @staticmethod
    def _parse_date_string(date_value: str) -> Optional[tuple]:
        if not isinstance(date_value, str):
            return None
        match = re.match(r"^(\d{4})\.(\d{1,2})\.(\d{1,2})$", date_value.strip())
        if not match:
            return None
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return year, month, day

    @staticmethod
    def _extract_date_from_filename(save_file: Path) -> Optional[tuple]:
        stem = save_file.stem
        match = re.search(r"_(\d{4})_(\d{1,2})_(\d{1,2})(?:_|$)", stem)
        if not match:
            return None
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return year, month, day

    def _enrich_timeline_metadata(self, data: Dict[str, Any], save_file: Path) -> Dict[str, Any]:
        """Ensure metadata has timeline info with configured fallback priority."""
        metadata = data.setdefault("metadata", {})
        metadata.setdefault("filename", save_file.name)

        # 1) Existing in-save metadata
        game_day = metadata.get("game_day")
        if game_day is not None:
            try:
                metadata["game_day"] = int(game_day)
                metadata.setdefault("timeline_source", "save_date")
                return metadata
            except (TypeError, ValueError):
                metadata.pop("game_day", None)

        # Save date present but game_day missing
        existing_date = metadata.get("date")
        parsed_date = self._parse_date_string(existing_date) if existing_date else None
        if parsed_date:
            year, month, day = parsed_date
            metadata["game_day"] = self._to_game_day(year, month, day)
            metadata.setdefault("timeline_source", "save_date")
            return metadata

        # 2) Filename-derived date
        filename_date = self._extract_date_from_filename(save_file)
        if filename_date:
            year, month, day = filename_date
            filename_date_str = f"{year}.{month}.{day}"
            filename_game_day = self._to_game_day(year, month, day)
            metadata["filename_date"] = filename_date_str
            metadata["filename_game_day"] = filename_game_day
            metadata.setdefault("date", filename_date_str)
            metadata.setdefault("game_day", filename_game_day)
            metadata.setdefault("timeline_source", "filename_date")
            return metadata

        # 3) File mtime fallback
        try:
            mtime_epoch = float(save_file.stat().st_mtime)
            metadata["file_mtime_epoch"] = mtime_epoch
            metadata["timeline_source"] = "file_mtime"
        except OSError:
            metadata["timeline_source"] = "index"

        return metadata

    @staticmethod
    def _next_unique_path(path: Path) -> Path:
        if not path.exists():
            return path

        idx = 1
        while True:
            candidate = path.with_name(f"{path.stem}_{idx}{path.suffix}")
            if not candidate.exists():
                return candidate
            idx += 1

    def _archive_processed_save(
        self,
        save_file: Path,
        playthrough_id: str,
        game_day: Optional[int],
        force_archive: bool = False,
        source_name: Optional[str] = None,
    ) -> bool:
        """Move processed save snapshot into archive storage."""
        source_label = (source_name or save_file.name).lower()
        if not force_archive and "autosave" not in source_label:
            return False
        if not save_file.exists():
            return False

        playthrough_archive = self.processed_saves_dir / playthrough_id
        playthrough_archive.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        source_stem = Path(source_name).stem if source_name else save_file.stem
        if game_day is not None:
            archive_name = f"{source_stem}_day{game_day}_{timestamp}{save_file.suffix}"
        else:
            archive_name = f"{source_stem}_{timestamp}{save_file.suffix}"
        destination = self._next_unique_path(playthrough_archive / archive_name)

        last_error = None
        for _ in range(12):
            try:
                shutil.move(str(save_file), str(destination))
                print(f"Archived save snapshot: {destination}")
                return True
            except (PermissionError, OSError) as e:
                last_error = e
                time.sleep(0.2)

        print(f"Warning: Could not archive save snapshot: {save_file} ({last_error})")
        return False

    def _get_signature(self, save_file: Path) -> Optional[Dict[str, int]]:
        """Get file signature used to detect actual file changes."""
        try:
            stat = save_file.stat()
        except (FileNotFoundError, PermissionError, OSError):
            return None

        mtime_ns = getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000))
        return {
            "mtime_ns": int(mtime_ns),
            "size": int(stat.st_size),
        }

    @staticmethod
    def _signature_key(signature: Dict[str, int]) -> str:
        return f"{signature.get('size', 0)}:{signature.get('mtime_ns', 0)}"

    @staticmethod
    def _signature_to_filename_fragment(signature: Dict[str, int]) -> str:
        return SaveMonitor._signature_key(signature).replace(":", "_")

    def _wait_for_file_stable(
        self,
        save_file: Path,
        debounce_seconds: float,
        timeout_seconds: float = 30.0,
    ) -> Optional[Dict[str, int]]:
        """Wait until file mtime/size stop changing for a short window."""
        poll_interval = 0.2
        stable_required = max(0.2, float(debounce_seconds))
        deadline = time.time() + timeout_seconds

        previous_sig = None
        stable_since = None

        while time.time() < deadline:
            signature = self._get_signature(save_file)
            if signature is None:
                previous_sig = None
                stable_since = None
                time.sleep(poll_interval)
                continue

            if signature == previous_sig:
                if stable_since is None:
                    stable_since = time.time()
                elif (time.time() - stable_since) >= stable_required:
                    return signature
            else:
                previous_sig = signature
                stable_since = time.time()

            time.sleep(poll_interval)

        return previous_sig

    @staticmethod
    def _copy_with_retries(source: Path, destination: Path, retries: int = 12, delay: float = 0.2) -> bool:
        last_error = None
        for _ in range(retries):
            try:
                shutil.copy2(str(source), str(destination))
                return True
            except (PermissionError, OSError) as e:
                last_error = e
                time.sleep(delay)
        print(f"Warning: Could not copy save snapshot: {source} ({last_error})")
        return False

    @staticmethod
    def _move_with_retries(source: Path, destination: Path, retries: int = 12, delay: float = 0.2) -> bool:
        last_error = None
        for _ in range(retries):
            try:
                shutil.move(str(source), str(destination))
                return True
            except (PermissionError, OSError) as e:
                last_error = e
                time.sleep(delay)
        print(f"Warning: Could not move save snapshot: {source} ({last_error})")
        return False

    def _capture_save_snapshot(
        self,
        source_file: Path,
        playthrough_id: str,
        stable_sig: Dict[str, int],
        reason: str,
    ) -> Optional[_QueuedSaveTask]:
        """Capture immutable save snapshot for later serialized processing."""
        queue_dir = self.queued_saves_dir / playthrough_id
        queue_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        sig_fragment = self._signature_to_filename_fragment(stable_sig)
        queue_name = f"{source_file.stem}_{timestamp}_{sig_fragment}{source_file.suffix}"
        queued_path = self._next_unique_path(queue_dir / queue_name)

        moved = False
        if self._is_autosave_file(source_file):
            moved = self._move_with_retries(source_file, queued_path)

        if not moved:
            if not source_file.exists():
                print(f"Warning: Save disappeared before snapshot capture: {source_file.name}")
                return None
            if not self._copy_with_retries(source_file, queued_path):
                return None

        task = _QueuedSaveTask(
            queued_path=queued_path,
            source_path=source_file,
            signature=stable_sig,
            playthrough_id=playthrough_id,
            queued_at_epoch=time.time(),
        )
        self._increment_stat("captured")
        print(f"Captured ({reason}): {source_file.name} -> {queued_path.name}")
        return task

    def _capture_save_task(self, source_file: Path, reason: str) -> Optional[_QueuedSaveTask]:
        """Stabilize + dedupe event and capture snapshot task."""
        source_file = Path(source_file)
        if not self._is_watch_target(source_file):
            return None
        if not source_file.exists():
            return None

        stable_sig = self._wait_for_file_stable(source_file, self._debounce_seconds)
        if stable_sig is None:
            self._increment_stat("error")
            print(f"Warning: Save did not stabilize in time: {source_file.name}")
            return None

        path_key = self._path_key(source_file)
        previous_sig = self.file_signatures.get(path_key)
        if previous_sig == stable_sig:
            self._increment_stat("event_duplicate_skipped")
            return None

        playthrough_id = self.identify_playthrough(source_file)
        task = self._capture_save_snapshot(source_file, playthrough_id, stable_sig, reason)
        if not task:
            self._increment_stat("error")
            return None

        self.file_signatures[path_key] = stable_sig
        self._save_state()
        return task

    def _process_save_file(
        self,
        save_file: Path,
        callback: Callable[[Path, str], Optional[Dict[str, Any]]],
        reason: str,
        source_file: Optional[Path] = None,
        stable_sig: Optional[Dict[str, int]] = None,
        playthrough_id: Optional[str] = None,
        force_archive: bool = False,
    ) -> bool:
        """Process a save file with timeline and dedupe fallback logic."""
        save_file = Path(save_file)
        source_file = Path(source_file) if source_file else save_file

        if not save_file.exists():
            return False

        # Direct mode keeps backwards compatibility for tests/manual calls.
        if stable_sig is None:
            if not self._is_watch_target(source_file):
                return False

            stable_sig = self._wait_for_file_stable(save_file, self._debounce_seconds)
            if stable_sig is None:
                self._increment_stat("error")
                return False

            path_key = self._path_key(source_file)
            previous_sig = self.file_signatures.get(path_key)
            if previous_sig == stable_sig:
                self.file_signatures[path_key] = stable_sig
                self._save_state()
                self._increment_stat("event_duplicate_skipped")
                return False

            self.file_signatures[path_key] = stable_sig
            self._save_state()

        if playthrough_id is None:
            playthrough_id = self.identify_playthrough(source_file)

        try:
            result = callback(save_file, playthrough_id)
        except ParserRuntimeUnavailableError as e:
            self._increment_stat("error")
            print(f"Native parser runtime unavailable ({save_file.name}): {e}")
            print("Action: reinstall/update analyzer build to restore bundled parser runtime.")
            return False
        except BinarySaveParseError as e:
            self._increment_stat("unsupported_format")
            print(f"Save parse failed ({save_file.name}): {e}")
            print("Action: save skipped; monitoring continues for next autosave.")
            return False
        except Exception as e:
            self._increment_stat("error")
            print(f"Error processing {save_file.name}: {e}")
            return False

        if not result:
            self._increment_stat("error")
            return False

        metadata = self._enrich_timeline_metadata(result, source_file)

        game_day = metadata.get("game_day")
        if game_day is not None:
            try:
                game_day = int(game_day)
                metadata["game_day"] = game_day
            except (TypeError, ValueError):
                game_day = None
                metadata.pop("game_day", None)

        data_recorded = True
        if game_day is not None:
            seen_days = self.seen_game_days.setdefault(playthrough_id, set())
            if game_day in seen_days:
                data_recorded = False
                self._increment_stat("duplicate_skipped")
                print(f"Skipping duplicate game day {game_day}: {source_file.name}")
            else:
                seen_days.add(game_day)
        else:
            sig_key = self._signature_key(stable_sig)
            if sig_key in self.seen_signature_keys:
                data_recorded = False
                self._increment_stat("duplicate_skipped")
                print(f"Skipping duplicate signature: {source_file.name}")
            else:
                self.seen_signature_keys.add(sig_key)

        if data_recorded:
            if playthrough_id not in self.tracking_data:
                self.tracking_data[playthrough_id] = []
            self.tracking_data[playthrough_id].append(result)
            self._save_data_point(playthrough_id, result)
            self._increment_stat("processed")

        self._save_state()

        # Queue snapshots are always archived; direct mode archives autosaves only.
        self._archive_processed_save(
            save_file,
            playthrough_id,
            game_day,
            force_archive=force_archive,
            source_name=source_file.name,
        )

        if data_recorded:
            print(f"Processed ({reason}): {source_file.name}")
        return data_recorded

    def _process_queued_task(self, task: _QueuedSaveTask, reason: str) -> bool:
        if not self._callback:
            return False

        return self._process_save_file(
            task.queued_path,
            self._callback,
            reason=reason,
            source_file=task.source_path,
            stable_sig=task.signature,
            playthrough_id=task.playthrough_id,
            force_archive=True,
        )

    def process_existing_saves(self, callback, reset_stats: bool = True) -> int:
        """Process all currently present saves with same capture/queue pipeline."""
        if reset_stats:
            self.reset_run_stats()

        save_files = self.get_save_files()
        if save_files:
            print(f"\nFound {len(save_files)} save file(s) to evaluate")

        processed_count = 0
        for save_file in save_files:
            try:
                task = self._capture_save_task(save_file, reason="startup_scan")
                if not task:
                    continue

                if self._process_save_file(
                    task.queued_path,
                    callback,
                    reason="startup_scan",
                    source_file=task.source_path,
                    stable_sig=task.signature,
                    playthrough_id=task.playthrough_id,
                    force_archive=True,
                ):
                    processed_count += 1
            except Exception as e:
                self._increment_stat("error")
                print(f"Error processing {save_file.name}: {e}")

        return processed_count

    def process_new_saves(self, callback):
        """Backward-compatible alias for old polling API."""
        return self.process_existing_saves(callback)

    def enqueue_event(self, save_file: Path):
        """Queue changed save file path for capture stage."""
        if not self.running:
            return
        if not self._is_watch_target(save_file):
            return

        self._event_queue.put(Path(save_file))

    def _capture_worker_loop(self):
        """Capture immutable save snapshots from raw filesystem events."""
        while True:
            try:
                item = self._event_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if item is self._EVENT_STOP:
                self._event_queue.task_done()
                break

            save_file = item
            try:
                task = self._capture_save_task(Path(save_file), reason="file_event")
                if task:
                    self._process_queue.put(task)
            except Exception as e:
                self._increment_stat("error")
                print(f"Capture worker error ({Path(save_file).name}): {e}")
            finally:
                self._event_queue.task_done()

    def _process_worker_loop(self):
        """Process queued save snapshots sequentially."""
        while True:
            try:
                item = self._process_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if item is self._PROCESS_STOP:
                self._process_queue.task_done()
                break

            task = item
            try:
                self._process_queued_task(task, reason="file_event")
            except Exception as e:
                self._increment_stat("error")
                print(f"Process worker error ({task.queued_path.name}): {e}")
            finally:
                self._process_queue.task_done()

    def _save_data_point(self, playthrough_id: str, data: Dict):
        """Save individual data point to JSON with collision-safe naming."""
        playthrough_dir = self.data_output_dir / playthrough_id
        playthrough_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = playthrough_dir / f"data_{timestamp}.json"

        collision_idx = 1
        while filename.exists():
            filename = playthrough_dir / f"data_{timestamp}_{collision_idx}.json"
            collision_idx += 1

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_playthrough_data(self, playthrough_id: str) -> List[Dict]:
        """Load all data for a specific playthrough."""
        playthrough_dir = self.data_output_dir / playthrough_id
        if not playthrough_dir.exists():
            return []

        data_points = []
        for json_file in sorted(playthrough_dir.glob("data_*.json")):
            with open(json_file, "r") as f:
                data_points.append(json.load(f))

        return data_points

    def get_all_playthroughs(self) -> List[str]:
        """Get list of all tracked playthroughs."""
        if not self.data_output_dir.exists():
            return []

        excluded = {"processed_saves", "queued_saves"}
        return [
            d.name
            for d in self.data_output_dir.iterdir()
            if d.is_dir() and d.name not in excluded
        ]

    def start_monitoring(self, callback, process_existing: bool = True, debounce_seconds: float = 1.5):
        """Start event-driven monitoring and return processed startup count."""
        if Observer is None:
            raise RuntimeError(
                "watchdog is not installed. Run: pip install -r requirements.txt"
            )
        if not self.save_directory.exists():
            raise FileNotFoundError(f"Save directory not found: {self.save_directory}")
        if self.running:
            return 0

        self.reset_run_stats()
        self._callback = callback
        self._debounce_seconds = max(0.2, float(debounce_seconds))
        self._event_queue = queue.Queue()
        self._process_queue = queue.Queue()

        startup_count = 0
        if process_existing:
            startup_count = self.process_existing_saves(callback, reset_stats=False)

        self.running = True
        self._capture_thread = threading.Thread(target=self._capture_worker_loop, daemon=True)
        self._capture_thread.start()

        self._process_thread = threading.Thread(target=self._process_worker_loop, daemon=True)
        self._process_thread.start()

        try:
            handler = _SaveFileEventHandler(self)
            self._observer = Observer()
            self._observer.schedule(handler, str(self.save_directory), recursive=False)
            self._observer.start()
        except Exception:
            self.running = False
            self._event_queue.put(self._EVENT_STOP)
            self._process_queue.put(self._PROCESS_STOP)
            if self._capture_thread:
                self._capture_thread.join(timeout=5)
                self._capture_thread = None
            if self._process_thread:
                self._process_thread.join(timeout=5)
                self._process_thread = None
            raise

        print(f"Started monitoring: {self.save_directory}")
        print("Watching folder continuously for save changes...")
        print("Capturing save snapshots and processing sequentially...")
        return startup_count

    def stop_monitoring(self):
        """Stop monitoring and drain queued snapshots before exit."""
        self.running = False

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        # Stop capture stage after all queued events have been consumed.
        self._event_queue.put(self._EVENT_STOP)
        if self._capture_thread:
            self._capture_thread.join(timeout=60)
            if self._capture_thread.is_alive():
                print("Warning: capture worker did not stop cleanly within timeout.")
            self._capture_thread = None

        # Stop process stage after captured snapshots are fully processed.
        self._process_queue.put(self._PROCESS_STOP)
        if self._process_thread:
            self._process_thread.join(timeout=120)
            if self._process_thread.is_alive():
                print("Warning: process worker did not stop cleanly within timeout.")
            self._process_thread = None

    def reset(self):
        """Reset all tracking data."""
        self.file_signatures.clear()
        self.seen_game_days.clear()
        self.seen_signature_keys.clear()
        self.tracking_data.clear()
        self.reset_run_stats()
        self._save_state()
        print("Monitoring state reset")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python save_monitor.py <save_directory>")
        print("\nExample:")
        print(r'python save_monitor.py "C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games"')
        sys.exit(1)

    monitor = SaveMonitor(sys.argv[1])
    print(f"Monitoring: {monitor.save_directory}")
    print(f"Found {len(monitor.get_save_files())} save files")
    print(f"Playthroughs: {monitor.get_all_playthroughs()}")
