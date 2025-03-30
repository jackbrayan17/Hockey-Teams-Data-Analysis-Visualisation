import json
import pandas as pd

def load_json_file(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def add_ids(data):
    """Add an ID to each object in the JSON data."""
    for index, item in enumerate(data):
        item['ID'] = index + 1  # Adding ID starting from 1
    return data

def convert_to_excel(data, filename):
    """Convert the JSON data to an Excel file."""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

def convert_to_csv(data, filename):
    """Convert the JSON data to an Excel file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    # Specify the JSON file path
    json_file_path = 'hockey_teams.json'  # Change this to your JSON file path

    # Load the JSON data
    data = load_json_file(json_file_path)

    # Add IDs to the JSON data
    modified_data = add_ids(data)

    # Print modified data
    print(json.dumps(modified_data, indent=4))

    # Convert modified data to Excel
    excel_file_name = 'teams_data.xlsx'
    csv_file_name = 'teams_data.csv'
    convert_to_csv(modified_data, csv_file_name)
    print(f"Data has been converted to CSV file: {csv_file_name}")
    convert_to_excel(modified_data, excel_file_name)
    print(f"Data has been converted to Excel file: {excel_file_name}")
