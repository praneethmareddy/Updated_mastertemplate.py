import collections
import csv

def clean_text(text):
    """Remove unwanted characters and normalize text, removing only newlines within cells."""
    return text.replace("\r", "").replace("\n", "").replace('"', '').replace("'", "").strip()

def parse_csv(file_path):
    """Parse CSV while handling multi-line sections, parameters, and values correctly."""
    sections = []
    current_section = None
    buffer_params = []  # Buffer to store multi-line parameters
    buffer_values = []  # Buffer to store multi-line values
    collecting_params = False  # Flag to track if we're collecting parameters
    section_data = {"name": None, "parameters": [], "values": []}

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            row = [clean_text(cell) for cell in row if cell.strip() or cell == ""]  # Keep empty strings in values

            if not row:
                continue  

            if row[0].startswith("@"):  # Section Name
                if section_data["name"]:  
                    sections.append(section_data)  # Store previous section
                current_section = row[0]  
                section_data = {"name": current_section, "parameters": [], "values": []}
                collecting_params = True
                buffer_params = []  # Reset buffer for parameters
                buffer_values = []  # Reset buffer for values
            elif collecting_params:  # Collecting Parameters
                if buffer_params and (row[0].startswith(",") or buffer_params[-1].endswith(",")):  
                    buffer_params.extend(row)  # Append multi-line parameters
                else:
                    buffer_params = row  # Reset buffer with new parameters

                if not row[-1].endswith(","):  # If last entry doesn't end with a comma, store parameters
                    section_data["parameters"].extend([p.strip() for p in ",".join(buffer_params).split(",")])
                    collecting_params = False
                    buffer_params = []  # Reset for values
            else:  # Collecting Values
                if buffer_values and (row[0].startswith(",") or buffer_values[-1].endswith(",")):  
                    buffer_values.extend(row)  # Append multi-line values
                else:
                    buffer_values = row  # Reset buffer with new values

                if not row[-1].endswith(","):  # If last entry doesn't end with a comma, store values
                    section_data["values"].extend([v.strip() for v in ",".join(buffer_values).split(",")])
                    buffer_values = []  # Reset after storing

    if section_data["name"]:  
        sections.append(section_data)  # Store last section

    return sections
