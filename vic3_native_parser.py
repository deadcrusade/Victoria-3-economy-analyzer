"""
Native Victoria 3 save parsing via bundled librakaly runtime.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ParserRuntimeUnavailableError(Exception):
    """Raised when bundled native parser runtime cannot be loaded or validated."""


class BinarySaveParseError(Exception):
    """Raised when a binary save cannot be parsed by the native parser."""


@dataclass
class NativeVic3ParseResult:
    """Binary save parse result returned by native parser."""

    melted_text: str
    meta_text: str
    is_binary: bool
    unknown_tokens: bool
    runtime_version: str


class _RakalyRuntime:
    """ctypes wrapper around bundled rakaly.dll."""

    def __init__(self):
        self._manifest = self._load_manifest()
        self._validate_platform()
        self._dll_path = self._resolve_library_path(self._manifest)
        self._validate_library_file(self._dll_path, self._manifest)
        self._lib = self._load_library(self._dll_path)
        self._configure_signatures(self._lib)

    @staticmethod
    def _base_dir() -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(getattr(sys, "_MEIPASS"))
        return Path(__file__).resolve().parent

    def _load_manifest(self) -> dict:
        manifest_path = self._base_dir() / "vendor" / "librakaly" / "manifest.json"
        if not manifest_path.exists():
            raise ParserRuntimeUnavailableError(
                f"Native parser manifest not found: {manifest_path}. Reinstall/update analyzer build."
            )

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:  # pragma: no cover - defensive
            raise ParserRuntimeUnavailableError(
                f"Could not read native parser manifest '{manifest_path}': {e}"
            ) from e

    @staticmethod
    def _validate_platform():
        if sys.platform != "win32":
            raise ParserRuntimeUnavailableError(
                "Native Vic3 parser currently supports Windows only in this build."
            )

        if ctypes.sizeof(ctypes.c_void_p) != 8:
            raise ParserRuntimeUnavailableError(
                "Native Vic3 parser requires 64-bit Python/runtime."
            )

    def _resolve_library_path(self, manifest: dict) -> Path:
        rel_path = manifest.get("relative_library_path")
        if not isinstance(rel_path, str) or not rel_path.strip():
            raise ParserRuntimeUnavailableError(
                "Native parser manifest missing 'relative_library_path'."
            )

        candidate = self._base_dir() / Path(rel_path)
        if candidate.exists():
            return candidate

        # Fallback for non-standard working directories.
        fallback = Path(__file__).resolve().parent / Path(rel_path)
        if fallback.exists():
            return fallback

        raise ParserRuntimeUnavailableError(
            f"Native parser runtime not found at expected path: {candidate}. "
            "Reinstall/update analyzer build."
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest().upper()

    def _validate_library_file(self, dll_path: Path, manifest: dict):
        expected_sha = manifest.get("sha256")
        if isinstance(expected_sha, str) and expected_sha.strip():
            actual_sha = self._sha256(dll_path)
            if actual_sha != expected_sha.strip().upper():
                raise ParserRuntimeUnavailableError(
                    f"Native parser checksum mismatch for {dll_path.name}. "
                    "Reinstall/update analyzer build."
                )

    @staticmethod
    def _load_library(dll_path: Path):
        try:
            return ctypes.WinDLL(str(dll_path))
        except OSError as e:
            raise ParserRuntimeUnavailableError(
                f"Failed to load native parser runtime '{dll_path}': {e}. "
                "Reinstall/update analyzer build."
            ) from e

    @staticmethod
    def _configure_signatures(lib):
        lib.rakaly_vic3_file.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        lib.rakaly_vic3_file.restype = ctypes.c_void_p

        lib.rakaly_file_error.argtypes = [ctypes.c_void_p]
        lib.rakaly_file_error.restype = ctypes.c_void_p

        lib.rakaly_file_value.argtypes = [ctypes.c_void_p]
        lib.rakaly_file_value.restype = ctypes.c_void_p

        lib.rakaly_free_file.argtypes = [ctypes.c_void_p]
        lib.rakaly_free_file.restype = None

        lib.rakaly_file_is_binary.argtypes = [ctypes.c_void_p]
        lib.rakaly_file_is_binary.restype = ctypes.c_bool

        lib.rakaly_file_meta.argtypes = [ctypes.c_void_p]
        lib.rakaly_file_meta.restype = ctypes.c_void_p

        lib.rakaly_file_meta_melt.argtypes = [ctypes.c_void_p]
        lib.rakaly_file_meta_melt.restype = ctypes.c_void_p

        lib.rakaly_file_melt.argtypes = [ctypes.c_void_p]
        lib.rakaly_file_melt.restype = ctypes.c_void_p

        lib.rakaly_melt_error.argtypes = [ctypes.c_void_p]
        lib.rakaly_melt_error.restype = ctypes.c_void_p

        lib.rakaly_melt_value.argtypes = [ctypes.c_void_p]
        lib.rakaly_melt_value.restype = ctypes.c_void_p

        lib.rakaly_free_melt.argtypes = [ctypes.c_void_p]
        lib.rakaly_free_melt.restype = None

        lib.rakaly_melt_data_length.argtypes = [ctypes.c_void_p]
        lib.rakaly_melt_data_length.restype = ctypes.c_size_t

        lib.rakaly_melt_write_data.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
        lib.rakaly_melt_write_data.restype = ctypes.c_size_t

        lib.rakaly_melt_is_verbatim.argtypes = [ctypes.c_void_p]
        lib.rakaly_melt_is_verbatim.restype = ctypes.c_bool

        lib.rakaly_melt_binary_unknown_tokens.argtypes = [ctypes.c_void_p]
        lib.rakaly_melt_binary_unknown_tokens.restype = ctypes.c_bool

        lib.rakaly_error_length.argtypes = [ctypes.c_void_p]
        lib.rakaly_error_length.restype = ctypes.c_int

        lib.rakaly_error_write_data.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_int,
        ]
        lib.rakaly_error_write_data.restype = ctypes.c_int

        lib.rakaly_free_error.argtypes = [ctypes.c_void_p]
        lib.rakaly_free_error.restype = None

    def _read_error(self, err_ptr: int) -> str:
        if not err_ptr:
            return "Unknown parser error"

        try:
            length = int(self._lib.rakaly_error_length(err_ptr))
            if length <= 0:
                return "Unknown parser error"

            buffer = (ctypes.c_char * length)()
            written = int(self._lib.rakaly_error_write_data(err_ptr, buffer, length))
            if written < 0:
                return "Unknown parser error"

            raw = bytes(buffer[:written])
            return raw.decode("utf-8", errors="replace")
        finally:
            self._lib.rakaly_free_error(err_ptr)

    @staticmethod
    def _decode_text(raw: bytes) -> str:
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="ignore")

    def _melt_result_to_text(self, melt_result_ptr: int, original_bytes: bytes = b"") -> tuple[str, bool]:
        err_ptr = self._lib.rakaly_melt_error(melt_result_ptr)
        if err_ptr:
            raise BinarySaveParseError(self._read_error(err_ptr))

        melt_ptr = self._lib.rakaly_melt_value(melt_result_ptr)
        if not melt_ptr:
            raise BinarySaveParseError("Native parser returned empty melt output")

        try:
            unknown_tokens = bool(self._lib.rakaly_melt_binary_unknown_tokens(melt_ptr))

            if bool(self._lib.rakaly_melt_is_verbatim(melt_ptr)):
                return self._decode_text(original_bytes), unknown_tokens

            data_len = int(self._lib.rakaly_melt_data_length(melt_ptr))
            if data_len <= 0:
                return "", unknown_tokens

            buffer = (ctypes.c_char * data_len)()
            copied = int(self._lib.rakaly_melt_write_data(melt_ptr, buffer, data_len))
            if copied != data_len:
                raise BinarySaveParseError(
                    f"Native parser failed to copy melt output (expected {data_len}, got {copied})"
                )

            raw = bytes(buffer[:data_len])
            return self._decode_text(raw), unknown_tokens
        finally:
            self._lib.rakaly_free_melt(melt_ptr)

    def parse_vic3_save(self, save_path: Path) -> NativeVic3ParseResult:
        try:
            save_bytes = save_path.read_bytes()
        except OSError as e:
            raise BinarySaveParseError(f"Could not read save file '{save_path.name}': {e}") from e

        raw_buffer = ctypes.create_string_buffer(save_bytes, len(save_bytes))
        file_result_ptr = self._lib.rakaly_vic3_file(raw_buffer, len(save_bytes))
        if not file_result_ptr:
            raise BinarySaveParseError("Native parser did not return a valid file handle")

        err_ptr = self._lib.rakaly_file_error(file_result_ptr)
        if err_ptr:
            raise BinarySaveParseError(self._read_error(err_ptr))

        file_ptr = self._lib.rakaly_file_value(file_result_ptr)
        if not file_ptr:
            raise BinarySaveParseError("Native parser returned null game file")

        try:
            is_binary = bool(self._lib.rakaly_file_is_binary(file_ptr))

            meta_text = ""
            meta_ptr = self._lib.rakaly_file_meta(file_ptr)
            if meta_ptr:
                meta_melt_result = self._lib.rakaly_file_meta_melt(meta_ptr)
                meta_text, _ = self._melt_result_to_text(meta_melt_result, b"")

            melt_result_ptr = self._lib.rakaly_file_melt(file_ptr)
            melted_text, unknown_tokens = self._melt_result_to_text(melt_result_ptr, save_bytes)

            return NativeVic3ParseResult(
                melted_text=melted_text,
                meta_text=meta_text,
                is_binary=is_binary,
                unknown_tokens=unknown_tokens,
                runtime_version=str(self._manifest.get("version", "unknown")),
            )
        finally:
            self._lib.rakaly_free_file(file_ptr)


_runtime_singleton: Optional[_RakalyRuntime] = None
_runtime_load_error: Optional[Exception] = None


def _get_runtime() -> _RakalyRuntime:
    global _runtime_singleton, _runtime_load_error

    if _runtime_singleton is not None:
        return _runtime_singleton

    if _runtime_load_error is not None:
        raise ParserRuntimeUnavailableError(str(_runtime_load_error)) from _runtime_load_error

    try:
        _runtime_singleton = _RakalyRuntime()
        return _runtime_singleton
    except Exception as e:
        _runtime_load_error = e
        if isinstance(e, ParserRuntimeUnavailableError):
            raise
        raise ParserRuntimeUnavailableError(f"Failed to initialize native parser runtime: {e}") from e


def is_binary_save_file(save_path: Path) -> bool:
    """Return True for Vic3 zip/binary save containers."""
    try:
        with open(save_path, "rb") as f:
            header = f.read(32)
    except OSError:
        return False

    return header.startswith(b"SAV") or zipfile.is_zipfile(save_path)


def parse_vic3_save(save_path: str | Path) -> NativeVic3ParseResult:
    """Parse a Victoria 3 save file using bundled librakaly runtime."""
    path = Path(save_path)
    runtime = _get_runtime()
    return runtime.parse_vic3_save(path)
