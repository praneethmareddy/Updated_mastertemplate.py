def clean_text(text):
    """Remove unwanted characters, excessive spaces, and newlines."""
    return " ".join(text.replace('"', '').replace("'", "").split())
def parse_csv(file_path):
    """Parse CSV handling multi-line sections and clean unnecessary delimiters."""
    sections = collections.defaultdict(lambda: {"parameters": [], "values": []})
    current_section = None
    parameter_mode = False  # Track if we are in parameter mode
    buffer = []  # Buffer for multi-line section names
    last_row = None  # Store the last processed row for merging

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            row = [clean_text(cell) for cell in row if cell.strip()]  # Clean and remove empty cells

            if not row:
                continue  # Skip empty rows

            # Merge with last row if necessary
            if last_row and (last_row[-1].endswith(",") or row[0].startswith(",")):
                last_row[-1] = last_row[-1].rstrip(",") + row[0].lstrip(",")
                last_row.extend(row[1:])
                continue  # Skip further processing and wait for the next row

            last_row = row  # Update last row reference

            if row[0].startswith("@"):  # Section Name
                if buffer:
                    current_section = clean_text("".join(buffer))  # Join multi-line section name
                    buffer = []
                else:
                    current_section = row[0]

                sections[current_section]["parameters"] = []  # Reset parameters
                sections[current_section]["values"] = []  # Reset values
                parameter_mode = True  # Expect parameters next
            elif parameter_mode:  # Parameter Line
                sections[current_section]["parameters"].extend(row)
                parameter_mode = False  # Switch to value mode
            else:  # Values
                sections[current_section]["values"].append(row)

    return sections
