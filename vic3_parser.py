"""
Victoria 3 Save File Parser
Parses Paradox-format save files into Python dictionaries
"""

import re
from typing import Any, Dict, List, Union
from pathlib import Path


class Vic3SaveParser:
    """Parser for Victoria 3 save files"""
    
    def __init__(self, save_path: str):
        self.save_path = Path(save_path)
        self.data = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse the save file and return structured data"""
        print(f"Parsing save file: {self.save_path.name}")
        
        with open(self.save_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract key sections we care about
        self.data = {
            'filename': self.save_path.name,
            'date': self._extract_date(content),
            'countries': self._extract_countries(content),
            'markets': self._extract_markets(content),
            'goods_prices': self._extract_goods_prices(content),
            'states': self._extract_states(content),
            'buildings': self._extract_buildings(content),
        }
        
        return self.data
    
    def _extract_date(self, content: str) -> str:
        """Extract current game date"""
        match = re.search(r'current_date\s*=\s*"?(\d{4}\.\d{1,2}\.\d{1,2})"?', content)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _extract_countries(self, content: str) -> List[Dict]:
        """Extract country data"""
        countries = []
        
        # Find countries section
        countries_section = re.search(r'countries\s*=\s*\{(.*?)\n\}(?=\n[a-z_]+=)', content, re.DOTALL)
        if not countries_section:
            return countries
        
        # Extract individual countries (simplified)
        country_blocks = re.findall(r'(\d+)\s*=\s*\{([^}]*?definition\s*=\s*"?([A-Z]{3})"?[^}]*?)\}', 
                                    countries_section.group(1), re.DOTALL)
        
        for country_id, country_data, tag in country_blocks[:50]:  # Limit for performance
            country = {
                'id': country_id,
                'tag': tag,
            }
            
            # Extract GDP if available
            gdp_match = re.search(r'gdp\s*=\s*([\d.]+)', country_data)
            if gdp_match:
                country['gdp'] = float(gdp_match.group(1))
            
            # Extract gold reserves
            gold_match = re.search(r'gold_reserves\s*=\s*([\d.]+)', country_data)
            if gold_match:
                country['gold'] = float(gold_match.group(1))
            
            countries.append(country)
        
        return countries
    
    def _extract_markets(self, content: str) -> List[Dict]:
        """Extract market data"""
        markets = []
        
        # Find markets section
        markets_section = re.search(r'market_manager\s*=\s*\{(.*?)\n\}(?=\n[a-z_]+=)', content, re.DOTALL)
        if not markets_section:
            return markets
        
        # Extract individual markets
        market_blocks = re.findall(r'database\s*=\s*\{[^}]*?(\d+)\s*=\s*\{(.*?)\n\t\t\}', 
                                   markets_section.group(1), re.DOTALL)
        
        for market_id, market_data in market_blocks[:20]:  # Limit for performance
            market = {
                'id': market_id,
            }
            
            # Extract market capital
            capital_match = re.search(r'market_capital\s*=\s*(\d+)', market_data)
            if capital_match:
                market['capital_state'] = capital_match.group(1)
            
            markets.append(market)
        
        return markets
    
    def _extract_goods_prices(self, content: str) -> Dict[str, float]:
        """Extract goods prices from markets"""
        prices = {}
        
        # Find buy and sell packages in markets
        # This is a simplified extraction - real format is more complex
        price_matches = re.findall(r'goods\s*=\s*"?([a-z_]+)"?\s+.*?price\s*=\s*([\d.]+)', content)
        
        for goods_type, price in price_matches:
            if goods_type not in prices or float(price) > 0:
                prices[goods_type] = float(price)
        
        return prices
    
    def _extract_states(self, content: str) -> List[Dict]:
        """Extract state data"""
        states = []
        
        # Find states section - this is complex, doing simplified version
        states_section = re.search(r'states\s*=\s*\{(.*?)\n\}(?=\n[a-z_]+=)', content, re.DOTALL)
        if not states_section:
            return states
        
        # Extract basic state info
        state_blocks = re.findall(r'(\d+)\s*=\s*\{[^}]*?state_region\s*=\s*"?([a-z_]+)"?[^}]*?\}', 
                                  states_section.group(1))
        
        for state_id, region_name in state_blocks[:100]:  # Limit for performance
            states.append({
                'id': state_id,
                'region': region_name,
            })
        
        return states
    
    def _extract_buildings(self, content: str) -> List[Dict]:
        """Extract building production data"""
        buildings = []
        
        # Find buildings section
        buildings_section = re.search(r'buildings\s*=\s*\{(.*?)\n\}(?=\n[a-z_]+=)', content, re.DOTALL)
        if not buildings_section:
            return buildings
        
        # Extract building types and their counts
        building_counts = {}
        building_matches = re.findall(r'building_type\s*=\s*"?([a-z_]+)"?', buildings_section.group(1))
        
        for building_type in building_matches:
            building_counts[building_type] = building_counts.get(building_type, 0) + 1
        
        return [{'type': k, 'count': v} for k, v in building_counts.items()]
    
    def get_summary(self) -> str:
        """Get a text summary of parsed data"""
        summary = []
        summary.append(f"Save File: {self.data.get('filename', 'Unknown')}")
        summary.append(f"Date: {self.data.get('date', 'Unknown')}")
        summary.append(f"Countries: {len(self.data.get('countries', []))}")
        summary.append(f"Markets: {len(self.data.get('markets', []))}")
        summary.append(f"Goods Tracked: {len(self.data.get('goods_prices', {}))}")
        summary.append(f"Building Types: {len(self.data.get('buildings', []))}")
        return "\n".join(summary)


def test_parser():
    """Test the parser with a sample save file"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vic3_parser.py <save_file_path>")
        print("\nExample Windows path:")
        print(r'python vic3_parser.py "C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games\autosave.v3"')
        return
    
    parser = Vic3SaveParser(sys.argv[1])
    data = parser.parse()
    print("\n" + "="*60)
    print(parser.get_summary())
    print("="*60)
    
    # Print some sample data
    if data.get('goods_prices'):
        print("\nSample Goods Prices:")
        for goods, price in list(data['goods_prices'].items())[:10]:
            print(f"  {goods}: {price:.2f}")
    
    if data.get('buildings'):
        print("\nTop Building Types:")
        sorted_buildings = sorted(data['buildings'], key=lambda x: x['count'], reverse=True)
        for building in sorted_buildings[:10]:
            print(f"  {building['type']}: {building['count']}")


if __name__ == "__main__":
    test_parser()
