"""
Manual binary parser validation against real Victoria 3 saves.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_extractor import BinarySaveParseError, EconomicExtractor, ParserRuntimeUnavailableError


def validate_save(save_file: Path):
    extractor = EconomicExtractor(str(save_file))
    data = extractor.extract_all()
    metadata = data.get("metadata", {})

    print("-" * 72)
    print(f"Save: {save_file.name}")
    print(f"Date: {metadata.get('date')}")
    print(f"Game Day: {metadata.get('game_day')}")
    print(f"Version: {metadata.get('game_version')}")
    print(f"Backend: {metadata.get('parse_backend')}")
    print(f"Save Format: {metadata.get('save_format')}")
    print(f"Unknown Tokens: {metadata.get('unknown_tokens')}")
    print(f"Goods Tracked: {len(data.get('goods_economy', {}))}")
    print(f"Price Crashes: {len(data.get('price_crashes', []))}")


def main():
    parser = argparse.ArgumentParser(description="Validate binary parser pipeline on Vic3 saves")
    parser.add_argument("save_dir", help="Path to Victoria 3 save games directory")
    parser.add_argument("--limit", type=int, default=3, help="How many saves to validate")
    args = parser.parse_args()

    save_dir = Path(args.save_dir)
    files = sorted(save_dir.glob("*.v3"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not files:
        print(f"No .v3 files found in: {save_dir}")
        return

    success = 0
    failures = 0
    for save_file in files[: max(1, args.limit)]:
        try:
            validate_save(save_file)
            success += 1
        except ParserRuntimeUnavailableError as e:
            failures += 1
            print(f"Runtime unavailable for {save_file.name}: {e}")
        except BinarySaveParseError as e:
            failures += 1
            print(f"Parse failed for {save_file.name}: {e}")
        except Exception as e:
            failures += 1
            print(f"Unexpected error for {save_file.name}: {e}")

    print("=" * 72)
    print(f"Validation complete: success={success}, failures={failures}")


if __name__ == "__main__":
    main()
