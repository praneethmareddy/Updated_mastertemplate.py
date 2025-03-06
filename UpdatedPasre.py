import csv
import collections
import re

def clean_text(text):
    """Remove unwanted characters and normalize text."""
    return text.strip().replace('"', '').replace("'", "").replace("\t", " ").replace("\n", " ")

def parse_csv(file_path):
    """Parse CSV handling multi-line sections and combined section names with parameters."""
    sections = collections.defaultdict(lambda: {"parameters": set(), "values": []})
    current_section = None
    parameter_mode = False
    buffer = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            if not row:
                continue  # Skip empty rows

            row = [clean_text(cell) for cell in row if cell.strip()]  # Clean and remove empty cells

            if not row:
                continue  # Skip if row becomes empty after cleaning

            if row[0].startswith("@"):  # Section Name
                if buffer:
                    current_section = clean_text("".join(buffer))
                    buffer = []
                else:
                    current_section = row[0]

                # Check for combined section name and parameters
                if '##' in current_section:
                    parts = current_section.split('##')
                    current_section = parts[0]
                    parameters = parts[1:] + row[1:]
                    sections[current_section]["parameters"].update(parameters)
                    parameter_mode = False
                else:
                    parameter_mode = True
            elif parameter_mode:
                sections[current_section]["parameters"].update(row)
                parameter_mode = False
            else:
                sections[current_section]["values"].append(row)

        if buffer:
            current_section = clean_text("".join(buffer))
            sections[current_section]["parameters"].update(row)

    # Convert parameter sets to lists to maintain consistency
    for section in sections:
        sections[section]["parameters"] = list(sections[section]["parameters"])

    return sections
