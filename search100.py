import os
import pandas as pd

def find_file4_nodes_equals_100(folder_path):
    matched_files = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".xlsx", ".xls")):
                file_path = os.path.join(root, file)

                try:
                    df = pd.read_excel(file_path)

                    # Check if the column exists
                    if "file4_nodes" in df.columns:
                        # Check if any value in the column == 100
                        if (df["file4_nodes"] == 100).any():
                            matched_files.append(file_path)

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return matched_files


# ----------------- USE THE FUNCTION -----------------

folder = r"/home/etud/Bureau/projet/fichiers/csp/generated_files_db/"  # <-- change this
results = find_file4_nodes_equals_100(folder)

print("Files where 'file4_nodes' contains the value 100:")
for f in results:
    print(f)
