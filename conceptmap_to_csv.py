import json
import csv
import os
import sys

def parse_conceptmap(conceptmap_path, output_dir):
    # Load ConceptMap JSON
    with open(conceptmap_path, 'r', encoding='utf-8') as f:
        conceptmap = json.load(f)

    # Prepare lists to hold source and target entries
    source_entries = []
    target_entries = []

    # Traverse the ConceptMap structure
    for group in conceptmap.get('group', []):
        source_system = group.get('source')
        target_system = group.get('target')

        for element in group.get('element', []):
            source_code = element.get('code')
            source_display = element.get('display')

            source_entries.append({
                'system': source_system,
                'code': source_code,
                'display': source_display or ''
            })

            for target in element.get('target', []):
                target_code = target.get('code')
                target_display = target.get('display')

                target_entries.append({
                    'system': target_system,
                    'code': target_code,
                    'display': target_display or ''
                })

    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write source codes to CSV
    source_csv_path = os.path.join(output_dir, 'source_codes.csv')
    with open(source_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['system', 'code', 'display'])
        writer.writeheader()
        writer.writerows(source_entries)

    # Write target codes to CSV
    target_csv_path = os.path.join(output_dir, 'target_codes.csv')
    with open(target_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['system', 'code', 'display'])
        writer.writeheader()
        writer.writerows(target_entries)

    print(f"Source codes written to: {source_csv_path}")
    print(f"Target codes written to: {target_csv_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python conceptmap_to_csv.py <ConceptMap.json> <OutputDirectory>")
        sys.exit(1)

    conceptmap_path = sys.argv[1]
    output_dir = sys.argv[2]

    parse_conceptmap(conceptmap_path, output_dir)

if __name__ == '__main__':
    main()
