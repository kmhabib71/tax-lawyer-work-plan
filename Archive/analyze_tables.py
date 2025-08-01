#!/usr/bin/env python3
"""
Analyze table structures in Bangladesh Laws documents
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_tables(url):
    """Analyze table structures with colspan/rowspan detection"""
    
    print(f"🔍 Analyzing tables in: {url}")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        print(f"📊 Found {len(tables)} tables")
        
        for i, table in enumerate(tables, 1):
            print(f"\n🏗️  TABLE {i}:")
            print("-" * 40)
            
            # Get table attributes
            table_attrs = table.attrs
            print(f"Table attributes: {table_attrs}")
            
            # Analyze rows
            rows = table.find_all('tr')
            print(f"Total rows: {len(rows)}")
            
            # Analyze each row
            for row_idx, row in enumerate(rows[:10]):  # First 10 rows
                cells = row.find_all(['td', 'th'])
                print(f"\nRow {row_idx + 1}: {len(cells)} cells")
                
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.get_text().strip()
                    if len(cell_text) > 50:
                        cell_text = cell_text[:50] + "..."
                    
                    colspan = cell.get('colspan', '1')
                    rowspan = cell.get('rowspan', '1')
                    
                    span_info = ""
                    if colspan != '1' or rowspan != '1':
                        span_info = f" [colspan={colspan}, rowspan={rowspan}]"
                    
                    cell_type = cell.name.upper()
                    print(f"  {cell_idx + 1}. [{cell_type}]{span_info} {cell_text}")
            
            if len(rows) > 10:
                print(f"... and {len(rows) - 10} more rows")
            
            # Check for nested tables
            nested_tables = table.find_all('table')
            if nested_tables:
                print(f"⚠️  Contains {len(nested_tables)} nested tables")
            
            # Save table HTML for inspection
            with open(f'table_{i}.html', 'w', encoding='utf-8') as f:
                f.write(str(table.prettify()))
            print(f"💾 Table HTML saved to: table_{i}.html")
        
        return tables
        
    except Exception as e:
        print(f"❌ Error analyzing {url}: {e}")
        return []

def main():
    url = "http://bdlaws.minlaw.gov.bd/act-details-1541.html"
    tables = analyze_tables(url)
    
    if tables:
        print(f"\n✅ Analysis complete! Found {len(tables)} tables")
        print(f"📄 Check table_*.html files for detailed structure")

if __name__ == "__main__":
    main()