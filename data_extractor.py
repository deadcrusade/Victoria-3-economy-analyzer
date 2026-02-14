"""
Economic Data Extractor for Victoria 3
Extracts and calculates economic metrics from parsed save data
"""

import re
from pathlib import Path
from typing import Any, Dict, List

from vic3_native_parser import (
    BinarySaveParseError,
    ParserRuntimeUnavailableError,
    is_binary_save_file,
    parse_vic3_save,
)


class UnsupportedSaveFormatError(BinarySaveParseError):
    """Deprecated compatibility alias. Use BinarySaveParseError instead."""


class EconomicExtractor:
    """Extracts economic metrics from Victoria 3 save files"""
    
    # Important goods to track
    KEY_GOODS = [
        'grain', 'meat', 'fish', 'groceries', 'fruit', 'liquor',  # Food
        'wood', 'iron', 'coal', 'sulfur', 'lead', 'oil',  # Raw materials
        'steel', 'tools', 'engines', 'explosives', 'fertilizer',  # Industrial
        'fabric', 'clothes', 'furniture', 'paper', 'luxury_clothes', 'luxury_furniture',  # Consumer
        'transportation', 'electricity', 'telecommunications',  # Infrastructure
        'glass', 'porcelain', 'services', 'luxury_goods',  # Luxury/Services
    ]

    _GOODS_INDEX_MAP = {
        0: "ammunition",
        1: "small_arms",
        2: "artillery",
        3: "manowars",
        4: "ironclads",
        5: "grain",
        6: "fish",
        7: "fabric",
        8: "wood",
        9: "coal",
        10: "iron",
        11: "tools",
        12: "sulfur",
        13: "steel",
        14: "engines",
        15: "glass",
        16: "lead",
        17: "hardwood",
        18: "paper",
        19: "clothes",
        20: "services",
        21: "electricity",
        22: "transportation",
        23: "luxury_clothes",
        24: "luxury_furniture",
        25: "furniture",
        26: "porcelain",
        27: "groceries",
        28: "fruit",
        29: "liquor",
        30: "wine",
        31: "meat",
        32: "sugar",
        33: "tea",
        34: "coffee",
        35: "silk",
        36: "dye",
        37: "opium",
        38: "oil",
        39: "rubber",
        40: "gold",
        41: "fine_art",
        42: "radios",
        43: "automobiles",
        44: "aeroplanes",
        45: "telephones",
        46: "fertilizer",
        47: "explosives",
        48: "steamers",
        49: "electric_gear",
        50: "tank",
    }
    
    def __init__(self, save_path: str):
        self.save_path = Path(save_path)
        self.raw_content = ""
        self.raw_meta_content = ""
        
    def extract_all(self) -> Dict[str, Any]:
        """Extract all economic data from save file"""
        print(f"Extracting economic data from: {self.save_path.name}")

        parse_backend = "regex_text"
        binary_result = None

        if self._is_binary_save():
            binary_result = parse_vic3_save(self.save_path)
            self.raw_content = binary_result.melted_text
            self.raw_meta_content = binary_result.meta_text or ""
            parse_backend = "librakaly"
        else:
            with open(self.save_path, "r", encoding="utf-8", errors="ignore") as f:
                self.raw_content = f.read()
            self.raw_meta_content = ""
        
        data = {
            'metadata': self._extract_metadata(),
            'goods_economy': self._extract_goods_economy(),
            'market_stockpiles': self._extract_market_stockpiles(),
            'production_methods': self._extract_production_methods(),
            'trade_routes': self._extract_trade_routes(),
            'building_profitability': self._extract_building_profitability(),
            'country_economies': self._extract_country_economies(),
        }
        
        # Calculate derived metrics
        data['overproduction_ratio'] = self._calculate_overproduction(data)
        data['price_crashes'] = self._identify_price_crashes(data)

        metadata = data.setdefault("metadata", {})
        metadata["parse_backend"] = parse_backend

        if binary_result is not None:
            metadata["save_format"] = "binary" if binary_result.is_binary else "text"
            metadata["unknown_tokens"] = bool(binary_result.unknown_tokens)
            metadata["parser_runtime_version"] = binary_result.runtime_version
        
        return data

    def _is_binary_save(self) -> bool:
        """Return True if save is a binary container handled by native parser."""
        return is_binary_save_file(self.save_path)
    
    def _extract_metadata(self) -> Dict:
        """Extract save file metadata"""
        metadata = {}

        # Date (prefer full melted gamestate, fallback to melted metadata)
        date_match = re.search(
            r'(?:current_date|game_date)\s*=\s*"?(\d{4}\.\d{1,2}\.\d{1,2})"?', self.raw_content
        )
        if not date_match and self.raw_meta_content:
            date_match = re.search(
                r'(?:current_date|game_date)\s*=\s*"?(\d{4}\.\d{1,2}\.\d{1,2})"?', self.raw_meta_content
            )
        if date_match:
            metadata['date'] = date_match.group(1)
            # Convert to days for easier tracking
            year, month, day = map(int, date_match.group(1).split('.'))
            metadata['game_day'] = (year - 1836) * 365 + (month - 1) * 30 + day
        
        # Game version
        version_match = re.search(r'version\s*=\s*"([^"]+)"', self.raw_content)
        if not version_match and self.raw_meta_content:
            version_match = re.search(r'version\s*=\s*"([^"]+)"', self.raw_meta_content)
        if version_match:
            metadata['game_version'] = version_match.group(1)
        
        metadata['filename'] = self.save_path.name
        
        return metadata
    
    def _extract_goods_economy(self) -> Dict[str, Dict]:
        """Extract production, consumption, and prices for all goods"""
        goods_data = {}
        
        # Extract prices from market packages
        # Format: goods = "goods_name" ... price = value
        # Keep this strict pass first, then fallback to a wider pass if needed.
        price_pattern = r'goods\s*=\s*"?([a-z_]+)"?\s+[^}]*?price\s*=\s*([-\d.]+)'
        for goods_name, price in re.findall(price_pattern, self.raw_content):
            if goods_name not in goods_data:
                goods_data[goods_name] = {}
            goods_data[goods_name]['price'] = float(price)
        
        # Extract buy/sell volumes (simplified)
        buy_pattern = r'goods\s*=\s*"?([a-z_]+)"?\s+[^}]*?quantity\s*=\s*([-\d.]+)[^}]*?price\s*=\s*([-\d.]+)'
        for goods_name, quantity, price in re.findall(buy_pattern, self.raw_content):
            if goods_name not in goods_data:
                goods_data[goods_name] = {}
            
            # Track volumes
            if 'buy_volume' not in goods_data[goods_name]:
                goods_data[goods_name]['buy_volume'] = 0
            goods_data[goods_name]['buy_volume'] += float(quantity)

            # Ensure price is still captured even when strict price pass missed it
            if 'price' not in goods_data[goods_name]:
                goods_data[goods_name]['price'] = float(price)

        # Fallback extraction for saves where formatting breaks strict regex assumptions.
        # Scan from each goods declaration and look ahead a short window.
        if not any(v.get('price', 0) > 0 for v in goods_data.values()):
            goods_decl = re.finditer(r'goods\s*=\s*"?([a-z_]+)"?', self.raw_content)
            for match in goods_decl:
                goods_name = match.group(1)
                snippet = self.raw_content[match.end():match.end() + 400]

                price_match = re.search(r'\bprice\s*=\s*([-\d.]+)', snippet)
                if not price_match:
                    continue

                if goods_name not in goods_data:
                    goods_data[goods_name] = {}
                goods_data[goods_name]['price'] = float(price_match.group(1))

        # Native melted Vic3 saves often expose market price reports keyed by goods index.
        if not any(v.get('price', 0) > 0 for v in goods_data.values()):
            indexed_goods = self._extract_indexed_goods_prices()
            for goods_name, price in indexed_goods.items():
                if goods_name not in goods_data:
                    goods_data[goods_name] = {}
                goods_data[goods_name]["price"] = price
        
        return goods_data

    def _extract_indexed_goods_prices(self) -> Dict[str, float]:
        """
        Extract average goods prices from index-based `current_price_report` blocks.
        Falls back to synthetic names if goods index mapping is unknown.
        """
        pattern = re.compile(
            r'(?m)^\s*(\d+)\s*=\s*\{\s*\n\s*value\s*=\s*([-\d.]+)\s*\n\s*prestige_goods\s*=\s*\{'
        )

        # Track report context so we only aggregate from market price report sections.
        report_anchor = "current_price_report={"
        report_positions = []
        start = 0
        while True:
            idx = self.raw_content.find(report_anchor, start)
            if idx < 0:
                break
            report_positions.append(idx)
            start = idx + len(report_anchor)

        if not report_positions:
            return {}

        values_by_index: Dict[int, List[float]] = {}
        report_idx = 0

        for match in pattern.finditer(self.raw_content):
            pos = match.start()
            if pos < report_positions[0]:
                continue

            while report_idx + 1 < len(report_positions) and report_positions[report_idx + 1] <= pos:
                report_idx += 1

            nearest_report = report_positions[report_idx]
            if pos < nearest_report:
                continue
            if pos - nearest_report > 12000:
                continue

            goods_index = int(match.group(1))
            value = float(match.group(2))
            values_by_index.setdefault(goods_index, []).append(value)

        goods_prices: Dict[str, float] = {}
        for goods_index, samples in values_by_index.items():
            if not samples:
                continue
            goods_name = self._GOODS_INDEX_MAP.get(goods_index, f"goods_{goods_index}")
            goods_prices[goods_name] = sum(samples) / len(samples)

        return goods_prices
    
    def _extract_market_stockpiles(self) -> Dict[str, float]:
        """Extract stockpiled goods in markets"""
        stockpiles = {}
        
        # Pattern: stockpile goods tracking
        stockpile_pattern = r'stockpile\s*=\s*\{[^}]*?goods\s*=\s*"?([a-z_]+)"?[^}]*?amount\s*=\s*([\d.]+)'
        
        for goods_name, amount in re.findall(stockpile_pattern, self.raw_content):
            if goods_name not in stockpiles:
                stockpiles[goods_name] = 0
            stockpiles[goods_name] += float(amount)
        
        return stockpiles
    
    def _extract_production_methods(self) -> Dict[str, int]:
        """Track which production methods are in use"""
        pm_usage = {}
        
        # Pattern: production_method_type = "pm_name"
        pm_pattern = r'production_method_type\s*=\s*"?([a-z_0-9_]+)"?'
        
        for pm_name in re.findall(pm_pattern, self.raw_content):
            pm_usage[pm_name] = pm_usage.get(pm_name, 0) + 1
        
        return pm_usage
    
    def _extract_trade_routes(self) -> List[Dict]:
        """Extract active trade routes"""
        routes = []
        
        # Simplified: count trade routes by goods type
        route_pattern = r'goods\s*=\s*"?([a-z_]+)"?[^}]*?level\s*=\s*(\d+)'
        
        route_counts = {}
        for goods_name, level in re.findall(route_pattern, self.raw_content):
            if goods_name not in route_counts:
                route_counts[goods_name] = {'count': 0, 'total_level': 0}
            route_counts[goods_name]['count'] += 1
            route_counts[goods_name]['total_level'] += int(level)
        
        for goods_name, data in route_counts.items():
            routes.append({
                'goods': goods_name,
                'route_count': data['count'],
                'total_level': data['total_level']
            })
        
        return routes
    
    def _extract_building_profitability(self) -> Dict[str, List[float]]:
        """Extract profitability metrics for buildings"""
        profitability = {}
        
        # Pattern: weekly profit/loss for buildings
        profit_pattern = r'building_type\s*=\s*"?([a-z_]+)"?[^}]{0,500}?weekly_profit\s*=\s*([-\d.]+)'
        
        for building_type, profit in re.findall(profit_pattern, self.raw_content):
            if building_type not in profitability:
                profitability[building_type] = []
            profitability[building_type].append(float(profit))
        
        # Calculate average profitability
        avg_profit = {}
        for building_type, profits in profitability.items():
            if profits:
                avg_profit[building_type] = {
                    'avg': sum(profits) / len(profits),
                    'count': len(profits),
                    'unprofitable_count': sum(1 for p in profits if p < 0)
                }
        
        return avg_profit
    
    def _extract_country_economies(self) -> List[Dict]:
        """Extract economic data for countries"""
        countries = []
        
        # Find countries with GDP data
        country_pattern = r'definition\s*=\s*"?([A-Z]{3})"?[^}]{0,1000}?gdp\s*=\s*([\d.]+)'
        
        for tag, gdp in re.findall(country_pattern, self.raw_content)[:50]:
            countries.append({
                'tag': tag,
                'gdp': float(gdp)
            })
        
        return countries
    
    def _calculate_overproduction(self, data: Dict) -> Dict[str, float]:
        """Calculate overproduction ratios for key goods"""
        ratios = {}
        
        goods_economy = data.get('goods_economy', {})
        stockpiles = data.get('market_stockpiles', {})
        
        for goods_name in self.KEY_GOODS:
            if goods_name in goods_economy:
                price = goods_economy[goods_name].get('price', 1.0)
                stockpile = stockpiles.get(goods_name, 0)
                
                # Low price + high stockpile = overproduction
                if price < 15.0:  # Base price is usually around 20-40
                    overproduction_score = stockpile / (price + 0.1)
                    ratios[goods_name] = overproduction_score
        
        return ratios
    
    def _identify_price_crashes(self, data: Dict) -> List[Dict]:
        """Identify goods with crashed prices"""
        crashes = []
        
        goods_economy = data.get('goods_economy', {})
        
        for goods_name, goods_data in goods_economy.items():
            price = goods_data.get('price', 0)
            
            # Price crash threshold (prices below 10 are usually crashes)
            if price > 0 and price < 10.0:
                crashes.append({
                    'goods': goods_name,
                    'price': price,
                    'severity': 10.0 - price
                })
        
        # Sort by severity
        crashes.sort(key=lambda x: x['severity'], reverse=True)
        
        return crashes
    
    def get_summary(self, data: Dict) -> str:
        """Generate a text summary of economic data"""
        lines = []
        
        metadata = data.get('metadata', {})
        lines.append(f"Date: {metadata.get('date', 'Unknown')}")
        lines.append(f"Game Day: {metadata.get('game_day', 0)}")
        lines.append("")
        
        # Goods prices
        goods_economy = data.get('goods_economy', {})
        lines.append(f"Goods Tracked: {len(goods_economy)}")
        
        # Price crashes
        crashes = data.get('price_crashes', [])
        if crashes:
            lines.append(f"\nPrice Crashes ({len(crashes)}):")
            for crash in crashes[:10]:
                lines.append(f"  {crash['goods']}: ${crash['price']:.2f}")
        
        # Overproduction
        overproduction = data.get('overproduction_ratio', {})
        if overproduction:
            lines.append(f"\nTop Overproduction Issues:")
            sorted_op = sorted(overproduction.items(), key=lambda x: x[1], reverse=True)[:10]
            for goods, ratio in sorted_op:
                lines.append(f"  {goods}: {ratio:.2f}")
        
        # Building profitability
        profitability = data.get('building_profitability', {})
        if profitability:
            unprofitable = {k: v for k, v in profitability.items() if v['avg'] < 0}
            lines.append(f"\nUnprofitable Building Types: {len(unprofitable)}/{len(profitability)}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_extractor.py <save_file_path>")
        sys.exit(1)
    
    extractor = EconomicExtractor(sys.argv[1])
    data = extractor.extract_all()
    
    print("\n" + "="*60)
    print(extractor.get_summary(data))
    print("="*60)
