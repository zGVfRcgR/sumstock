#!/usr/bin/env python3
"""
Generate index.md pages for prefecture and city directories
to create proper navigation hierarchy in Jekyll site.
"""

import os
import sys
from pathlib import Path


def generate_prefecture_index(pref_path: Path, pref_name: str):
    """Generate index.md for a prefecture directory"""
    index_path = pref_path / "index.md"
    
    content = f"""---
layout: default
title: {pref_name}
parent: データ一覧
has_children: true
nav_order: 10
---

# {pref_name}

このページには{pref_name}の市町村別データが表示されています。

各市町村を選択してデータをご覧ください。
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {index_path}")


def generate_city_index(city_path: Path, city_name: str, pref_name: str):
    """Generate index.md for a city directory"""
    index_path = city_path / "index.md"
    
    content = f"""---
layout: default
title: {city_name}
parent: {pref_name}
has_children: true
nav_order: 10
---

# {city_name}

このページには{pref_name}{city_name}の日付別データが表示されています。

各日付を選択してデータをご覧ください。
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {index_path}")


def update_data_file_frontmatter(data_file: Path, city_name: str):
    """Update front matter in data files to set proper parent"""
    with open(data_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and update the parent line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('parent:'):
            lines[i] = f'parent: {city_name}\n'
            updated = True
            break
    
    if updated:
        with open(data_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False


def main():
    """Main function to generate all index pages"""
    # Get the data directory
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        # Default to data directory in repository
        repo_root = Path(__file__).parent.parent
        data_dir = repo_root / "data"
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing data directory: {data_dir}")
    
    # Track statistics
    stats = {
        'prefecture_indexes': 0,
        'city_indexes': 0,
        'data_files_updated': 0
    }
    
    # Process each prefecture directory
    for pref_path in data_dir.iterdir():
        if not pref_path.is_dir():
            continue
        
        pref_name = pref_path.name
        
        # Skip hidden directories and existing index
        if pref_name.startswith('.'):
            continue
        
        print(f"\nProcessing prefecture: {pref_name}")
        
        # Generate prefecture index
        generate_prefecture_index(pref_path, pref_name)
        stats['prefecture_indexes'] += 1
        
        # Process each city directory
        for city_path in pref_path.iterdir():
            if not city_path.is_dir():
                continue
            
            city_name = city_path.name
            
            # Skip hidden directories
            if city_name.startswith('.'):
                continue
            
            print(f"  Processing city: {city_name}")
            
            # Generate city index
            generate_city_index(city_path, city_name, pref_name)
            stats['city_indexes'] += 1
            
            # Update data files in this city
            for data_file in city_path.glob("*.md"):
                # Skip index files
                if data_file.name == "index.md":
                    continue
                
                if update_data_file_frontmatter(data_file, city_name):
                    stats['data_files_updated'] += 1
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Prefecture indexes created: {stats['prefecture_indexes']}")
    print(f"City indexes created: {stats['city_indexes']}")
    print(f"Data files updated: {stats['data_files_updated']}")
    print("\nIndex generation complete!")


if __name__ == '__main__':
    main()
