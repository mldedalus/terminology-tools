# Setting up the tool
This only needs done once, thereafter all you need to do is ensure the virtual environment is active before running
## Create virtual environment (venv) called toolsevn
```
python3 -m venv toolsenv
```

## Activate the new virtual environment
```
source toolsenv/bin/activate
```

## Install Dependencies
```
pip install -r dependencies.txt
```

## Configure Secrets
The tool may need to contact a terminology server to do things such as look up display values. Please ensure the /config/secrets.yaml is populated.


# Usage
## Convert ConceptMap into CSVs.
This script takes a ConceptMap and creates two CSVs - one for the source codes, and one for the target codes

_Example Usage_
```
python3 conceptmap_to_csv.py ~/work/onelondon/EMIS_to_SNOMED_DrugCodeID_cm.json ./output/ 
```
This would create two CSVs in the output folder:
* source_codes.csv
* target_codes.csv

## Fetch Code Displays
This script takes a CSV containing a system/code and fetches the display if it is empty.

_Example Usage_
```
python3 retrieve_display_from_csv.py ./output/target_codes.csv ./output/target_codes_with_display.csv
```
This would produce a CSV with the display code from the given FHIR Server.
It does batches of 500 codes to the Codesystem/$lookup operation via POST.


