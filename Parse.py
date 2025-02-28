import collections
import csv

def clean_text(text):
    """Remove unwanted characters and normalize text, removing only newlines within cells."""
    return text.replace("\r", "").replace("\n", "").replace('"', '').replace("'", "").strip()

def parse_csv(file_path):
    """Parse CSV while handling multi-line sections, parameters, and values correctly."""
    sections = []
    current_section = None
    collecting_params = False
    buffer = []  # Buffer to store multi-line parameters or values
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
                buffer = []  # Reset buffer for parameters
            elif collecting_params:  # Collecting Parameters
                if buffer and (row[0].startswith(",") or buffer[-1].endswith(",")):  
                    buffer.extend(row)  # Append multi-line parameters
                else:
                    buffer = row  # Reset buffer with new parameters

                if not row[-1].endswith(","):  # If last entry doesn't end with a comma, store parameters
                    section_data["parameters"] = [p.strip() for p in ",".join(buffer).split(",")]
                    collecting_params = False
                    buffer = []  # Reset for values
            else:  # Collecting Values
                if buffer and (row[0].startswith(",") or buffer[-1].endswith(",")):  
                    buffer.extend(row)  # Append multi-line values
                else:
                    buffer = row  # Reset buffer with new values

                if not row[-1].endswith(","):  # If last entry doesn't end with a comma, store values
                    section_data["values"] = [v.strip() for v in ",".join(buffer).split(",")]
                    buffer = []  # Reset after storing

    if section_data["name"]:  
        sections.append(section_data)  # Store last section

    return sections
