import csv
import os
import sys
import requests
import yaml
from helpers import authentication

invalid_code_systems = []
batch_size = 500

def build_lookup_bundle(rows_to_update):
    bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "entry": []
    }
    for system, code in rows_to_update:
        entry = {
            "request": {
                "method": "POST",
                "url": "CodeSystem/$lookup"
            },
            "resource": {
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "system", "valueUri": system},
                    {"name": "code", "valueCode": code}
                ]
            }
        }
        bundle["entry"].append(entry)
    return bundle

def send_lookup_bundle(bundle, terminology_server_url, access_token):
    url = f"{terminology_server_url.rstrip('/')}/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/fhir+json',
        'Accept': 'application/fhir+json'
    }
    response = requests.post(url, headers=headers, json=bundle)
    response.raise_for_status()
    return response.json()

def parse_bundle_response(response):
    display_map = {}
    for entry in response.get('entry', []):
        outcome = entry.get('resource', {})
        if outcome.get('resourceType') == 'Parameters':
            system = None
            code = None
            display = None
            for param in outcome.get('parameter', []):
                if param.get('name') == 'system':
                    system = param.get('valueUri')
                elif param.get('name') == 'code':
                    code = param.get('valueCode')
                elif param.get('name') == 'display':
                    display = param.get('valueString')
            if system and code:
                display_map[(system, code)] = display
    return display_map

def parse_and_update_csv(csv_path, output_csv_path, client_id, client_secret, token_url, terminology_server_url):
    token = authentication.fetch_token(token_url, client_id, client_secret)

    updated_rows = []
    rows_to_update = []

    with open(csv_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            system = row.get('system')
            code = row.get('code')
            display = row.get('display')

            if not display:
                rows_to_update.append((system, code))
            updated_rows.append(row)

    display_map = {}

    if len(rows_to_update) > 0:
        
        for i in range(0, len(rows_to_update), batch_size):
            print(f"Processing batch {i // batch_size + 1} of {len(rows_to_update) // batch_size + 1}")
            batch = rows_to_update[i:i+batch_size]
            bundle = build_lookup_bundle(batch)
            response = send_lookup_bundle(bundle, terminology_server_url, token)
            batch_display_map = parse_bundle_response(response)
            display_map.update(batch_display_map)

        for row in updated_rows:
            if not row.get('display'):
                row['display'] = display_map.get((row.get('system'), row.get('code')), '') or ''

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['system', 'code', 'display'], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Updated CSV written to: {output_csv_path}")



def main():
    if len(sys.argv) != 3:
        print("Usage: python3 retrieve_display_from_csv.py <input.csv> <output.csv>")
        sys.exit(1)

    with open('./config/secrets.yaml', 'r') as f:
        secrets = yaml.safe_load(f)

    if 'client_id' not in secrets or secrets['client_id']=="":
        raise ValueError("client_id not found in config/secrets.yml, or value is empty")
    if 'client_secret' not in secrets or secrets['client_secret']=="":
        raise ValueError("client_secret not found in config/secrets.yml, or value is empty")
    if 'fhirEndpoint' not in secrets or secrets['fhirEndpoint']=="":
        raise ValueError("fhirEndpoint not found in config/secrets.yml, or value is empty")
    if 'authenticationEndpoint' not in secrets or secrets['authenticationEndpoint']=="":
        raise ValueError("authenticationEndpoint not found in config/secrets.yml, or value is empty")

    client_id = secrets['client_id']
    client_secret = secrets['client_secret']
    terminology_server_url = secrets['fhirEndpoint']
    token_url = secrets['authenticationEndpoint']

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    parse_and_update_csv(input_csv, output_csv, client_id, client_secret, token_url, terminology_server_url)

if __name__ == '__main__':
    main()
