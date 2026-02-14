import threading
import time
import unittest
from pathlib import Path
from uuid import uuid4

from save_monitor import SaveMonitor


class MonitorQueueingTests(unittest.TestCase):
    def _create_monitor(self):
        root = Path(".tmp_tests") / f"monitor_queue_{uuid4().hex}"
        save_dir = root / "saves"
        data_dir = root / "data"
        save_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        monitor = SaveMonitor(str(save_dir), data_output_dir=str(data_dir))
        monitor._debounce_seconds = 0.2
        return monitor, save_dir

    def _start_workers(self, monitor: SaveMonitor):
        monitor.running = True
        capture_thread = threading.Thread(target=monitor._capture_worker_loop, daemon=True)
        process_thread = threading.Thread(target=monitor._process_worker_loop, daemon=True)
        capture_thread.start()
        process_thread.start()
        return capture_thread, process_thread

    def _stop_workers(self, monitor: SaveMonitor, capture_thread: threading.Thread, process_thread: threading.Thread):
        monitor.running = False
        monitor._event_queue.put(monitor._EVENT_STOP)
        capture_thread.join(timeout=5)
        monitor._process_queue.put(monitor._PROCESS_STOP)
        process_thread.join(timeout=5)

    def test_same_slot_rewrite_while_processing_is_busy(self):
        monitor, save_dir = self._create_monitor()
        callback_started = threading.Event()
        processed_days = []

        def callback(save_file: Path, _playthrough_id: str):
            content = save_file.read_text(encoding="utf-8")
            day = int(content.split("=")[1])
            processed_days.append(day)
            if day == 1:
                callback_started.set()
                time.sleep(0.8)
            return {"metadata": {"game_day": day}}

        monitor._callback = callback
        capture_thread, process_thread = self._start_workers(monitor)
        try:
            autosave = save_dir / "autosave_1.v3"
            autosave.write_text("day=1", encoding="utf-8")
            monitor.enqueue_event(autosave)

            self.assertTrue(callback_started.wait(timeout=5))

            autosave.write_text("day=2", encoding="utf-8")
            monitor.enqueue_event(autosave)

            deadline = time.time() + 8
            while time.time() < deadline:
                if monitor.get_run_stats_snapshot().get("processed", 0) >= 2:
                    break
                time.sleep(0.1)

            stats = monitor.get_run_stats_snapshot()
            self.assertEqual(stats.get("processed"), 2)
            self.assertEqual(sorted(processed_days), [1, 2])
            self.assertEqual(stats.get("captured"), 2)
        finally:
            self._stop_workers(monitor, capture_thread, process_thread)

    def test_duplicate_event_burst_is_captured_once(self):
        monitor, save_dir = self._create_monitor()

        manual_save = save_dir / "manual_save.v3"
        manual_save.write_text("day=10", encoding="utf-8")

        first_task = monitor._capture_save_task(manual_save, reason="test_burst")
        second_task = monitor._capture_save_task(manual_save, reason="test_burst")
        third_task = monitor._capture_save_task(manual_save, reason="test_burst")

        stats = monitor.get_run_stats_snapshot()
        self.assertIsNotNone(first_task)
        self.assertIsNone(second_task)
        self.assertIsNone(third_task)
        self.assertEqual(stats.get("captured"), 1)
        self.assertGreaterEqual(stats.get("event_duplicate_skipped", 0), 2)


if __name__ == "__main__":
    unittest.main()
