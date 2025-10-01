#!/usr/bin/env python3
"""
Automatically scan the data folder and update datasets.json with all CSV files.
Run this script whenever you add new CSV files to the data folder.
"""

import os
import json
import glob

def update_datasets_manifest():
    """Scan data folder for CSV files and update datasets.json"""
    data_folder = 'data'

    if not os.path.exists(data_folder):
        print(f"Error: {data_folder} folder not found!")
        return

    # Find all CSV files in the data folder
    csv_files = []
    for file in os.listdir(data_folder):
        if file.endswith('.csv') and not file.startswith('.'):
            csv_files.append(file)

    # Sort alphabetically for consistency
    csv_files.sort()

    # Create datasets manifest
    manifest = {
        "datasets": csv_files,
        "last_updated": "auto-generated",
        "total_datasets": len(csv_files)
    }

    # Write to datasets.json
    manifest_path = os.path.join(data_folder, 'datasets.json')
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        print(f"✅ Successfully updated {manifest_path}")
        print(f"📊 Found {len(csv_files)} CSV datasets:")
        for i, dataset in enumerate(csv_files, 1):
            print(f"   {i}. {dataset}")

    except Exception as e:
        print(f"❌ Error writing manifest file: {e}")

if __name__ == "__main__":
    update_datasets_manifest()