import collections
import csv

def clean_text(text):
    """Remove newlines without adding spaces and preserve commas correctly."""
    return text.replace("\r", "").replace("\n", "").replace('"', '').replace("'", "").strip()

def parse_csv(file_path):
    """Parse CSV while handling multi-line sections, parameters, and values correctly."""
    sections = collections.defaultdict(lambda: {"parameters": set(), "values": []})
    current_section = None
    parameter_mode = False  
    last_row = []  # Store the last row to handle merging
    pending_merge = False  # Track if the last row needs merging

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            row = [clean_text(cell) for cell in row if cell.strip()]  # Clean and remove empty cells

            if not row:
                continue  

            # If last row ended with a comma OR current row starts with a comma, merge them
            if pending_merge or (last_row and last_row[-1].endswith(",")) or row[0].startswith(","):
                if last_row:
                    last_row[-1] = last_row[-1].rstrip(",") + row[0]  # Merge first element of new row
                    last_row.extend(row[1:])  # Append the rest
                pending_merge = row[-1].endswith(",")  # Check if merge is still needed
                continue  

            # Normal case: store current row as last_row
            last_row = row  
            pending_merge = row[-1].endswith(",")  # Check if merge is needed next iteration

            if row[0].startswith("@"):  # Section Name
                current_section = row[0]
                parameter_mode = True  
            elif parameter_mode:  # Parameter line
                sections[current_section]["parameters"].update(row)
                parameter_mode = False  
            else:  # Value line
                sections[current_section]["values"].append(row)

    return sections
