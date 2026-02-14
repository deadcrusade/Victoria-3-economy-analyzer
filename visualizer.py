"""
Matplotlib Visualizer for Victoria 3 Economic Data
Creates charts and graphs for economic analysis
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec


class EconomicVisualizer:
    """Creates visualizations for Victoria 3 economic data."""

    def __init__(self, output_dir: str = "./visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set style
        plt.style.use("seaborn-v0_8-darkgrid")

    @staticmethod
    def _extract_price(goods_data: Any) -> float:
        """Extract numeric price value from goods record shape."""
        if isinstance(goods_data, dict):
            value = goods_data.get("price", 0)
        else:
            value = goods_data

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _coerce_int(value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _resolve_timeline(self, metadata: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Resolve a point's timeline with priority: game_day > filename_game_day > mtime > index."""
        game_day = self._coerce_int(metadata.get("game_day"))
        if game_day is not None:
            return {
                "source": "game_day",
                "sort_value": float(game_day),
                "raw_value": game_day,
            }

        filename_game_day = self._coerce_int(metadata.get("filename_game_day"))
        if filename_game_day is not None:
            return {
                "source": "filename_game_day",
                "sort_value": float(filename_game_day),
                "raw_value": filename_game_day,
            }

        file_mtime_epoch = self._coerce_float(metadata.get("file_mtime_epoch"))
        if file_mtime_epoch is not None:
            return {
                "source": "file_mtime",
                "sort_value": file_mtime_epoch,
                "raw_value": file_mtime_epoch,
            }

        return {
            "source": "index",
            "sort_value": float(index),
            "raw_value": index,
        }

    @staticmethod
    def _timeline_sort_key(item: Dict[str, Any]) -> Tuple[int, float, int]:
        source = item["source"]
        if source in {"game_day", "filename_game_day"}:
            source_rank = 0
        elif source == "file_mtime":
            source_rank = 1
        else:
            source_rank = 2
        return source_rank, float(item["sort_value"]), int(item["index"])

    @staticmethod
    def _infer_axis_mode(items: List[Dict[str, Any]], preferred_mode: Optional[str] = None) -> str:
        allowed_modes = {"game_day", "save_time", "index"}
        if preferred_mode in allowed_modes:
            return preferred_mode

        has_day = any(i["source"] in {"game_day", "filename_game_day"} for i in items)
        if has_day:
            return "game_day"

        has_time = any(i["source"] == "file_mtime" for i in items)
        if has_time:
            return "save_time"

        return "index"

    def _build_x_values(self, ordered_items: List[Dict[str, Any]], axis_mode: str) -> List[Any]:
        x_values: List[Any] = []

        if axis_mode == "game_day":
            last_day: Optional[int] = None
            for seq, item in enumerate(ordered_items):
                source = item["source"]
                if source in {"game_day", "filename_game_day"}:
                    day = int(item["raw_value"])
                    last_day = day
                    x_values.append(day)
                    continue

                if last_day is None:
                    day = seq
                else:
                    day = last_day + 1
                last_day = day
                x_values.append(day)
            return x_values

        if axis_mode == "save_time":
            synthetic_anchor = datetime(1836, 1, 1)
            for seq, item in enumerate(ordered_items):
                source = item["source"]
                if source == "file_mtime":
                    x_values.append(datetime.fromtimestamp(float(item["raw_value"])))
                elif source in {"game_day", "filename_game_day"}:
                    x_values.append(synthetic_anchor + timedelta(days=int(item["raw_value"])))
                else:
                    x_values.append(synthetic_anchor + timedelta(minutes=seq))
            return x_values

        return list(range(len(ordered_items)))

    def _prepare_timeline(
        self,
        playthrough_data: List[Dict[str, Any]],
        preferred_mode: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Any], str, str]:
        """Sort data points and return plot-ready x values and axis metadata."""
        resolved_items = []
        for idx, data_point in enumerate(playthrough_data):
            metadata = data_point.get("metadata", {})
            timeline = self._resolve_timeline(metadata, idx)
            timeline["index"] = idx
            timeline["point"] = data_point
            resolved_items.append(timeline)

        ordered_items = sorted(resolved_items, key=self._timeline_sort_key)
        axis_mode = self._infer_axis_mode(ordered_items, preferred_mode)
        x_values = self._build_x_values(ordered_items, axis_mode)

        if axis_mode == "game_day":
            axis_label = "Game Day"
        elif axis_mode == "save_time":
            axis_label = "Save Time"
        else:
            axis_label = "Save Index"

        ordered_points = [item["point"] for item in ordered_items]
        return ordered_points, x_values, axis_mode, axis_label

    @staticmethod
    def _apply_time_axis(ax):
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))

    @staticmethod
    def _format_time_label(value: Any, axis_mode: str) -> str:
        if axis_mode == "game_day":
            return f"Day {int(value)}"
        if axis_mode == "save_time" and isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return f"#{int(value) + 1}"

    def plot_goods_prices_over_time(
        self,
        playthrough_data: List[Dict[str, Any]],
        goods_list: List[str] = None,
        playthrough_name: str = "default",
    ):
        """Plot goods prices over time."""
        if not playthrough_data:
            print("No data to plot")
            return

        ordered_data, timeline_x, axis_mode, axis_label = self._prepare_timeline(playthrough_data)

        all_goods = sorted(
            {
                goods_name
                for data_point in ordered_data
                for goods_name in data_point.get("goods_economy", {}).keys()
            }
        )
        discovered_prices = {goods_name: [] for goods_name in all_goods}

        for data_point in ordered_data:
            goods_economy = data_point.get("goods_economy", {})
            for goods_name in all_goods:
                goods_data = goods_economy.get(goods_name, {})
                discovered_prices[goods_name].append(self._extract_price(goods_data))

        if goods_list is None:
            prices = {
                goods_name: series
                for goods_name, series in discovered_prices.items()
                if any(p > 0 for p in series)
            }
        else:
            prices = {}
            for goods_name in goods_list:
                series = discovered_prices.get(goods_name, [0.0] * len(ordered_data))
                prices[goods_name] = series

            has_requested_data = any(any(p > 0 for p in series) for series in prices.values())
            if not has_requested_data:
                prices = {
                    goods_name: series
                    for goods_name, series in discovered_prices.items()
                    if any(p > 0 for p in series)
                }
                if prices:
                    print("Requested key goods missing; using all detected goods from data instead.")

        if not prices:
            print("No goods price data found to plot")
            return

        fig, ax = plt.subplots(figsize=(14, 8))

        for goods, price_list in prices.items():
            if any(p > 0 for p in price_list):
                ax.plot(timeline_x, price_list, marker="o", label=goods, linewidth=2)

        ax.set_xlabel(axis_label, fontsize=12)
        ax.set_ylabel("Price", fontsize=12)
        ax.set_title(f"Goods Prices Over Time - {playthrough_name}", fontsize=14, fontweight="bold")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)

        if axis_mode == "save_time":
            self._apply_time_axis(ax)
            fig.autofmt_xdate()

        filename = self.output_dir / f"{playthrough_name}_prices_over_time.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved: {filename}")
        plt.close()

    def plot_price_crashes(self, playthrough_data: List[Dict[str, Any]], playthrough_name: str = "default"):
        """Plot price crash severity over time."""
        if not playthrough_data:
            return

        ordered_data, timeline_x, axis_mode, axis_label = self._prepare_timeline(playthrough_data)

        crash_counts = []
        avg_severity = []

        for data_point in ordered_data:
            crashes = data_point.get("price_crashes", [])
            crash_counts.append(len(crashes))

            if crashes:
                avg_sev = sum(c.get("severity", 0) for c in crashes) / len(crashes)
                avg_severity.append(avg_sev)
            else:
                avg_severity.append(0)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        ax1.plot(timeline_x, crash_counts, marker="o", color="red", linewidth=2)
        ax1.fill_between(timeline_x, crash_counts, alpha=0.3, color="red")
        ax1.set_ylabel("Number of Price Crashes", fontsize=12)
        ax1.set_title(f"Price Crash Analysis - {playthrough_name}", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        ax2.plot(timeline_x, avg_severity, marker="s", color="orange", linewidth=2)
        ax2.fill_between(timeline_x, avg_severity, alpha=0.3, color="orange")
        ax2.set_xlabel(axis_label, fontsize=12)
        ax2.set_ylabel("Average Crash Severity", fontsize=12)
        ax2.grid(True, alpha=0.3)

        if axis_mode == "save_time":
            self._apply_time_axis(ax1)
            self._apply_time_axis(ax2)
            fig.autofmt_xdate()

        filename = self.output_dir / f"{playthrough_name}_price_crashes.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved: {filename}")
        plt.close()

    def plot_overproduction_heatmap(self, playthrough_data: List[Dict[str, Any]], playthrough_name: str = "default"):
        """Create heatmap of overproduction issues."""
        if not playthrough_data:
            return

        ordered_data, timeline_x, axis_mode, axis_label = self._prepare_timeline(playthrough_data)

        all_goods = set()
        for data_point in ordered_data:
            overproduction = data_point.get("overproduction_ratio", {})
            all_goods.update(overproduction.keys())

        if not all_goods:
            print("No overproduction data to plot")
            return

        goods_list = sorted(list(all_goods))[:20]

        matrix = []
        for goods in goods_list:
            row = []
            for data_point in ordered_data:
                overproduction = data_point.get("overproduction_ratio", {})
                row.append(overproduction.get(goods, 0))
            matrix.append(row)

        fig, ax = plt.subplots(figsize=(14, 10))
        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", interpolation="nearest")

        tick_step = max(1, len(timeline_x) // 20)
        tick_positions = list(range(0, len(timeline_x), tick_step))
        if tick_positions[-1] != len(timeline_x) - 1:
            tick_positions.append(len(timeline_x) - 1)

        tick_labels = [self._format_time_label(timeline_x[i], axis_mode) for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha="right")
        ax.set_yticks(range(len(goods_list)))
        ax.set_yticklabels(goods_list)

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Overproduction Ratio", rotation=270, labelpad=20)

        ax.set_title(f"Overproduction Heatmap - {playthrough_name}", fontsize=14, fontweight="bold", pad=20)
        ax.set_xlabel(axis_label, fontsize=12)
        ax.set_ylabel("Goods", fontsize=12)

        filename = self.output_dir / f"{playthrough_name}_overproduction_heatmap.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved: {filename}")
        plt.close()

    def plot_building_profitability(self, playthrough_data: List[Dict[str, Any]], playthrough_name: str = "default"):
        """Plot building profitability trends."""
        if not playthrough_data:
            return

        ordered_data, timeline_x, axis_mode, axis_label = self._prepare_timeline(playthrough_data)

        unprofitable_pct = []
        total_buildings = []

        for data_point in ordered_data:
            profitability = data_point.get("building_profitability", {})
            if profitability:
                total = len(profitability)
                unprofitable = sum(1 for v in profitability.values() if v.get("avg", 0) < 0)
                unprofitable_pct.append((unprofitable / total) * 100 if total > 0 else 0)
                total_buildings.append(total)
            else:
                unprofitable_pct.append(0)
                total_buildings.append(0)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        ax1.plot(timeline_x, unprofitable_pct, marker="o", color="crimson", linewidth=2)
        ax1.fill_between(timeline_x, unprofitable_pct, alpha=0.3, color="crimson")
        ax1.set_ylabel("Unprofitable Buildings (%)", fontsize=12)
        ax1.set_title(f"Building Profitability Trends - {playthrough_name}", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=50, color="red", linestyle="--", alpha=0.5, label="50% threshold")
        ax1.legend()

        ax2.plot(timeline_x, total_buildings, marker="s", color="steelblue", linewidth=2)
        ax2.set_xlabel(axis_label, fontsize=12)
        ax2.set_ylabel("Building Types Tracked", fontsize=12)
        ax2.grid(True, alpha=0.3)

        if axis_mode == "save_time":
            self._apply_time_axis(ax1)
            self._apply_time_axis(ax2)
            fig.autofmt_xdate()

        filename = self.output_dir / f"{playthrough_name}_building_profitability.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved: {filename}")
        plt.close()

    def plot_comparison_dashboard(self, playthrough_data_dict: Dict[str, List[Dict[str, Any]]]):
        """Create comparison dashboard across multiple playthroughs."""
        if not playthrough_data_dict:
            return

        per_playthrough = {}
        modes = []
        for playthrough_name, data in playthrough_data_dict.items():
            ordered_data, _, mode, _ = self._prepare_timeline(data)
            per_playthrough[playthrough_name] = ordered_data
            modes.append(mode)

        if "game_day" in modes:
            global_mode = "game_day"
            axis_label = "Game Day"
        elif "save_time" in modes:
            global_mode = "save_time"
            axis_label = "Save Time"
        else:
            global_mode = "index"
            axis_label = "Save Index"

        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])
        ax4 = fig.add_subplot(gs[2, :])

        for playthrough_name, ordered_data in per_playthrough.items():
            _, timeline_x, _, _ = self._prepare_timeline(ordered_data, preferred_mode=global_mode)

            crash_counts = [len(dp.get("price_crashes", [])) for dp in ordered_data]
            ax1.plot(timeline_x, crash_counts, marker="o", label=playthrough_name, linewidth=2)

            avg_prices = []
            for dp in ordered_data:
                goods_economy = dp.get("goods_economy", {})
                if goods_economy:
                    prices = []
                    for goods_entry in goods_economy.values():
                        price = self._extract_price(goods_entry)
                        if price > 0:
                            prices.append(price)
                    avg_prices.append(np.mean(prices) if prices else 0)
                else:
                    avg_prices.append(0)
            ax2.plot(timeline_x, avg_prices, marker="o", label=playthrough_name, linewidth=2)

            unprofitable_pct = []
            for dp in ordered_data:
                profitability = dp.get("building_profitability", {})
                if profitability:
                    total = len(profitability)
                    unprofitable = sum(1 for v in profitability.values() if v.get("avg", 0) < 0)
                    unprofitable_pct.append((unprofitable / total) * 100 if total > 0 else 0)
                else:
                    unprofitable_pct.append(0)
            ax3.plot(timeline_x, unprofitable_pct, marker="o", label=playthrough_name, linewidth=2)

            overproduction_counts = [len(dp.get("overproduction_ratio", {})) for dp in ordered_data]
            ax4.plot(timeline_x, overproduction_counts, marker="o", label=playthrough_name, linewidth=2)

        ax1.set_ylabel("Number of Price Crashes")
        ax1.set_title("Price Crashes Comparison", fontweight="bold", fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.set_ylabel("Average Price")
        ax2.set_title("Average Goods Prices", fontweight="bold", fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.set_ylabel("Unprofitable Buildings (%)")
        ax3.set_title("Building Profitability", fontweight="bold", fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        ax4.set_xlabel(axis_label)
        ax4.set_ylabel("Goods with Overproduction")
        ax4.set_title("Overproduction Issues", fontweight="bold", fontsize=12)
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        if global_mode == "save_time":
            self._apply_time_axis(ax1)
            self._apply_time_axis(ax2)
            self._apply_time_axis(ax3)
            self._apply_time_axis(ax4)
            fig.autofmt_xdate()

        filename = self.output_dir / "comparison_dashboard.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved: {filename}")
        plt.close()

    def generate_all_visualizations(
        self,
        playthrough_data: List[Dict[str, Any]],
        playthrough_name: str = "default",
        key_goods: List[str] = None,
    ):
        """Generate all standard visualizations."""
        print(f"\nGenerating visualizations for: {playthrough_name}")
        print("=" * 60)

        if key_goods is None:
            print("Plotting prices for all detected goods")
        else:
            print(f"Plotting prices for selected goods: {len(key_goods)}")

        self.plot_goods_prices_over_time(playthrough_data, key_goods, playthrough_name)
        self.plot_price_crashes(playthrough_data, playthrough_name)
        self.plot_overproduction_heatmap(playthrough_data, playthrough_name)
        self.plot_building_profitability(playthrough_data, playthrough_name)

        print("=" * 60)
        print(f"All visualizations saved to: {self.output_dir}")


if __name__ == "__main__":
    print("Visualizer module loaded successfully")
