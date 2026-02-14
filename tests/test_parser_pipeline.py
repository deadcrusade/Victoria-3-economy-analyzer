import unittest
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

from data_extractor import (
    BinarySaveParseError,
    EconomicExtractor,
    ParserRuntimeUnavailableError,
)
from vic3_native_parser import NativeVic3ParseResult


class ExtractorBinaryPipelineTests(unittest.TestCase):
    def _make_text_save(self, content: str) -> Path:
        tmpdir = Path(".tmp_tests") / f"parser_pipeline_{uuid4().hex}"
        tmpdir.mkdir(parents=True, exist_ok=True)
        path = tmpdir / "sample.v3"
        path.write_text(content, encoding="utf-8")
        return path

    def test_text_save_schema(self):
        save_path = self._make_text_save(
            'current_date=1850.5.1\nversion="1.12.4"\ngoods="grain" price=20\n'
        )

        data = EconomicExtractor(str(save_path)).extract_all()

        self.assertIn("metadata", data)
        self.assertIn("goods_economy", data)
        self.assertIn("market_stockpiles", data)
        self.assertIn("production_methods", data)
        self.assertIn("trade_routes", data)
        self.assertIn("building_profitability", data)
        self.assertIn("country_economies", data)
        self.assertIn("overproduction_ratio", data)
        self.assertIn("price_crashes", data)

    @patch("data_extractor.is_binary_save_file", return_value=True)
    @patch("data_extractor.parse_vic3_save")
    def test_binary_path_schema_with_indexed_prices(self, mock_parse, _mock_binary):
        save_path = self._make_text_save("dummy")

        mock_parse.return_value = NativeVic3ParseResult(
            melted_text=(
                'meta_data={version="1.12.4" game_date=1855.9.3}\n'
                'current_price_report={\n'
                '\tgoods={\n'
                '\t\t0={\n\t\t\tvalue=50\n\t\t\tprestige_goods={\n\t\t\t\t0 0 0\n\t\t\t}\n\t\t}\n'
                '\t}\n'
                '}\n'
            ),
            meta_text='meta_data={version="1.12.4" game_date=1855.9.3}',
            is_binary=True,
            unknown_tokens=False,
            runtime_version="0.12.5",
        )

        data = EconomicExtractor(str(save_path)).extract_all()

        self.assertIn("metadata", data)
        self.assertIn("goods_economy", data)
        self.assertGreater(len(data["goods_economy"]), 0)
        self.assertEqual(data["metadata"].get("parse_backend"), "librakaly")
        self.assertEqual(data["metadata"].get("save_format"), "binary")

    @patch("data_extractor.is_binary_save_file", return_value=True)
    @patch("data_extractor.parse_vic3_save", side_effect=ParserRuntimeUnavailableError("missing runtime"))
    def test_binary_runtime_error_passthrough(self, _mock_parse, _mock_binary):
        save_path = self._make_text_save("dummy")

        with self.assertRaises(ParserRuntimeUnavailableError):
            EconomicExtractor(str(save_path)).extract_all()

    @patch("data_extractor.is_binary_save_file", return_value=True)
    @patch("data_extractor.parse_vic3_save", side_effect=BinarySaveParseError("parse failed"))
    def test_binary_parse_error_passthrough(self, _mock_parse, _mock_binary):
        save_path = self._make_text_save("dummy")

        with self.assertRaises(BinarySaveParseError):
            EconomicExtractor(str(save_path)).extract_all()


if __name__ == "__main__":
    unittest.main()
