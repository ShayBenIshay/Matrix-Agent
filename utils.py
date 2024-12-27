import json
from datetime import datetime, timedelta

def convert_to_object(data_string):
    try:
        return json.loads(data_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def get_date_x_days_ago(x):
    target_date = datetime.now() - timedelta(days=x)
    return target_date.strftime("%Y-%m-%d")

def parse_portfolio(table_string):
    table_part = table_string.split('\n\n')[0]

    # Split the string into lines and strip each line to clean it up
    lines = table_part.strip().split('\n')

    # Extract headers from the first line (removing the | and whitespace)
    headers = [header.strip().lower() for header in lines[0].split('|') if header.strip()]

    # Process data rows
    data_rows = []
    for line in lines[2:]:  # Skip header and separator lines
        row_values = [value.strip() for value in line.split('|') if value.strip()]
        row_dict = dict(zip(headers, row_values))
        data_rows.append(row_dict)

    return data_rows