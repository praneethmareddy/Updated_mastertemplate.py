import os  
import zipfile  
import csv  
import collections  
import pandas as pd  
import seaborn as sns  
import matplotlib.pyplot as plt  

def extract_zip(zip_path, extract_to):  
    """Extract ZIP file to a directory."""  
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:  
        zip_ref.extractall(extract_to)  

def clean_text(text):  
    """Remove unwanted characters and normalize text."""  
    return text.strip().replace('"', '').replace("'", "").replace("\t", " ").replace("\n", " ")  

def parse_csv(file_path):  
    """Parse CSV handling multi-line sections and clean unnecessary delimiters."""  
    sections = collections.defaultdict(lambda: {"parameters": set(), "values": []})  
    current_section = None  
    parameter_mode = False  
    buffer = []  

    with open(file_path, 'r', encoding='utf-8') as f:  
        reader = csv.reader(f)  

        for row in reader:  
            if not row:  
                continue  

            row = [clean_text(cell) for cell in row if cell.strip()]  

            if not row:  
                continue  

            if row[0].startswith("@"):  
                if buffer:  
                    current_section = clean_text("".join(buffer))  
                    buffer = []  
                else:  
                    current_section = row[0]  

                parameter_mode = True  
            elif parameter_mode:  
                sections[current_section]["parameters"].update(row)  
                parameter_mode = False  
            else:  
                sections[current_section]["values"].append(row)  

        if buffer:  
            current_section = clean_text("".join(buffer))  
            sections[current_section]["parameters"].update(row)  

    return sections  

def process_operator(operator_dir):  
    """Process all CSVs for a given operator."""  
    section_counts = collections.defaultdict(int)  
    templates = collections.defaultdict(lambda: collections.defaultdict(set))  
    csv_param_sets = {}  

    for root, _, files in os.walk(operator_dir):  
        for file in files:  
            file_path = os.path.join(root, file)  

            if file.endswith(".zip"):  
                extract_to = os.path.join(root, file.replace(".zip", ""))  
                extract_zip(file_path, extract_to)  
              
            elif file.endswith(".csv"):  
                sections = parse_csv(file_path)  

                if sections:  
                    first_section = next(iter(sections))  
                    section_counts[first_section] += 1  

                    csv_params = set()  
                    for sec, data in sections.items():  
                        templates[sec]["parameters"].update(data["parameters"])  
                        csv_params.update(data["parameters"])  

                    csv_param_sets[file] = csv_params  

    return section_counts, templates, csv_param_sets  

def merge_templates(templates):  
    """Merge all section structures into a master template."""  
    return {section: list(data["parameters"]) for section, data in templates.items()}  

def save_master_template(operator, template, output_dir):  
    """Save master template as a TXT file."""  
    os.makedirs(output_dir, exist_ok=True)  
    file_path = os.path.join(output_dir, f"master_template_{operator}.txt")  

    with open(file_path, "w", encoding="utf-8") as f:  
        for section, params in template.items():  
            f.write(f"{section}\n")  
            f.write(", ".join(params) + "\n\n")  

    print(f"Master template saved: {file_path}")  

def process_all_operators(base_directory, output_dir):  
    """Process each operator and generate master templates."""  
    operator_master_templates = {}  
    operator_section_counts = {}  
    operator_param_sets = {}  

    for operator in os.listdir(base_directory):  
        operator_path = os.path.join(base_directory, operator)  
        if os.path.isdir(operator_path):  
            print(f"Processing Operator: {operator}")  

            section_counts, templates, csv_param_sets = process_operator(operator_path)  
            operator_master_templates[operator] = merge_templates(templates)  
            operator_section_counts[operator] = section_counts  
            operator_param_sets[operator] = csv_param_sets  

            save_master_template(operator, operator_master_templates[operator], output_dir)  

    return operator_master_templates, operator_section_counts, operator_param_sets  

def merge_global_master(operators_templates):  
    """Combine all operator templates into a single global master template without sorting or duplicates."""  
    global_template = collections.defaultdict(list)  

    for templates in operators_templates.values():  
        for section, params in templates.items():  
            seen = set(global_template[section])  
            for param in params:  
                if param not in seen:  
                    global_template[section].append(param)  
                    seen.add(param)  

    return dict(global_template)  

def save_global_master_template(global_template, output_dir):  
    """Save the global master template as a TXT file, preserving order."""  
    file_path = os.path.join(output_dir, "global_master_template.txt")  

    with open(file_path, "w", encoding="utf-8") as f:  
        for section, params in global_template.items():  
            f.write(f"{section}\n")  
            f.write(", ".join(params) + "\n\n")  

    print(f"Global master template saved: {file_path}")  

def analyze_common_parameters(operator_param_sets):  
    """Analyze and visualize common parameters within each operator and across operators."""  
    operator_common_params = {}  
    global_param_sets = []  

    for operator, csv_param_sets in operator_param_sets.items():  
        if csv_param_sets:  
            common_params = set.intersection(*csv_param_sets.values())  
            operator_common_params[operator] = common_params  
            global_param_sets.append(set.union(*csv_param_sets.values()))  

            print(f"\nOperator: {operator}")  
            print("Total Parameters per CSV:")  
            for csv_file, param_set in csv_param_sets.items():  
                print(f"{csv_file}: {len(param_set)}")  

            print(f"Common Parameters in all CSVs: {len(common_params)}\n")  

            plt.figure(figsize=(8, 6))  
            csv_files = list(csv_param_sets.keys())  
            param_matrix = [[len(csv_param_sets[f1] & csv_param_sets[f2]) for f2 in csv_files] for f1 in csv_files]  
            sns.heatmap(param_matrix, annot=True, cmap="Blues", xticklabels=csv_files, yticklabels=csv_files)  
            plt.title(f"Parameter Similarity Heatmap - {operator}")  
            plt.xlabel("CSV Files")  
            plt.ylabel("CSV Files")  
            plt.show()  

    global_common_params = set.intersection(*global_param_sets) if global_param_sets else set()  
    print("\n### Global Common Parameters Across All Operators ###")  
    print("Total Unique Parameters Per Operator:")  
    for operator, param_set in operator_common_params.items():  
        print(f"{operator}: {len(param_set)}")  

    print(f"Common Parameters Across Operators: {len(global_common_params)}")  

def analyze_section_distribution(operator_section_counts):  
    """Display section type distribution across operators."""  
    section_df = pd.DataFrame(operator_section_counts).fillna(0).astype(int)  
    print("\n### Section Type Distribution Across Operators ###")  
    print(section_df)  

    section_df.T.plot(kind='bar', stacked=True, figsize=(10, 6), colormap="viridis")  
    plt.title("Section Type Distribution Across Operators")  
    plt.xlabel("Operators")  
    plt.ylabel("Section Count")  
    plt.legend(title="Section Type", bbox_to_anchor=(1, 1))  
    plt.show()  

def main():  
    base_directory = "path/to/your/directory"  
    output_dir = "path/to/output/directory"  

    operator_templates, operator_counts, operator_param_sets = process_all_operators(base_directory, output_dir)  

    analyze_common_parameters(operator_param_sets)  
    analyze_section_distribution(operator_counts)  

    global_master_template = merge_global_master(operator_templates)  
    save_global_master_template(global_master_template, output_dir)  

if __name__ == "__main__":  
    main()
