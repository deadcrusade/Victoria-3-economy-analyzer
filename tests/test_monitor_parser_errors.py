import unittest
from pathlib import Path
from uuid import uuid4

from data_extractor import BinarySaveParseError, ParserRuntimeUnavailableError
from save_monitor import SaveMonitor


class MonitorParserErrorTests(unittest.TestCase):
    def _create_monitor(self):
        root = Path('.tmp_tests') / f"monitor_errors_{uuid4().hex}"
        save_dir = root / 'saves'
        data_dir = root / 'data'
        save_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        monitor = SaveMonitor(str(save_dir), data_output_dir=str(data_dir))
        monitor._debounce_seconds = 0.2
        return monitor, save_dir

    def test_runtime_error_counting(self):
        monitor, save_dir = self._create_monitor()
        save_file = save_dir / 'autosave_1.v3'
        save_file.write_bytes(b'SAV0100test')

        def cb(_save_file, _playthrough):
            raise ParserRuntimeUnavailableError('runtime missing')

        recorded = monitor._process_save_file(save_file, cb, reason='test_runtime_error')
        stats = monitor.get_run_stats_snapshot()

        self.assertFalse(recorded)
        self.assertEqual(stats.get('error'), 1)
        self.assertEqual(stats.get('unsupported_format'), 0)

    def test_parse_error_counting(self):
        monitor, save_dir = self._create_monitor()
        save_file = save_dir / 'autosave_2.v3'
        save_file.write_bytes(b'SAV0100test')

        def cb(_save_file, _playthrough):
            raise BinarySaveParseError('parse failed')

        recorded = monitor._process_save_file(save_file, cb, reason='test_parse_error')
        stats = monitor.get_run_stats_snapshot()

        self.assertFalse(recorded)
        self.assertEqual(stats.get('unsupported_format'), 1)


if __name__ == '__main__':
    unittest.main()
