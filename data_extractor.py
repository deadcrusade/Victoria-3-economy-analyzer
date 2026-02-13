"""
Economic Data Extractor for Victoria 3
Extracts and calculates economic metrics from parsed save data
"""

import re
from typing import Dict, List, Any
from pathlib import Path


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
    
    def __init__(self, save_path: str):
        self.save_path = Path(save_path)
        self.raw_content = ""
        
    def extract_all(self) -> Dict[str, Any]:
        """Extract all economic data from save file"""
        print(f"Extracting economic data from: {self.save_path.name}")
        
        # Read file
        with open(self.save_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.raw_content = f.read()
        
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
        
        return data
    
    def _extract_metadata(self) -> Dict:
        """Extract save file metadata"""
        metadata = {}
        
        # Date
        date_match = re.search(r'current_date\s*=\s*"?(\d{4}\.\d{1,2}\.\d{1,2})"?', self.raw_content)
        if date_match:
            metadata['date'] = date_match.group(1)
            # Convert to days for easier tracking
            year, month, day = map(int, date_match.group(1).split('.'))
            metadata['game_day'] = (year - 1836) * 365 + (month - 1) * 30 + day
        
        # Game version
        version_match = re.search(r'version\s*=\s*"([^"]+)"', self.raw_content)
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
        
        return goods_data
    
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
