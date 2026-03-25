import pandas as pd

# === Load files ===
file_linescols_path = "/home/etud/Bureau/projet/indicators_lines_cols/run_class_b_15082025152720/results.xlsx"
file_pos_path = "/home/etud/Bureau/projet/indicators_pos/run_10092025142625/results.xlsx"
classfile_path = "/home/etud/Bureau/projet/fichiers/csp/generated_files_db/class_b_28072025080534.xlsx"

file_classes = pd.read_excel(classfile_path)
file_pos = pd.read_excel(file_pos_path)
file_linescols = pd.read_excel(file_linescols_path)

# === Step 1: Extract all graph names into a mapping ===
graph_to_group = {}
for idx, row in file_classes.iterrows():
    group = set()
    for col in file_classes.columns:
        if "name" in col:
            val = row[col]
            if pd.notna(val):
                group.add(val)
    for name in group:
        graph_to_group[name] = group

# === Step 2: Create lookup from file_pos results ===
file_pos_lookup = {
    (row["Pattern"], row["Target"]): row["Sols"]
    for _, row in file_pos.iterrows()
}

# === Step 3: For each row in file_linescols, find Sols from file_pos for group member ===
sols_from_file_pos = []
for idx, row in file_linescols.iterrows():
    target = row["Target"]
    pattern = row["Pattern"]
    sols_val = None
    if target in graph_to_group:
        group = graph_to_group[target]
        for member in group:
            key = (pattern, member)
            if key in file_pos_lookup:
                sols_val = file_pos_lookup[key]
                break
    sols_from_file_pos.append(sols_val)

# === Step 4: Add results to file_linescols dataframe ===
file_linescols["Sols_file_pos"] = sols_from_file_pos
# === Step 5: Add difference column (Sols_file_pos - Sols) ===
file_linescols["Sols"] = pd.to_numeric(file_linescols["Sols"], errors="coerce")
file_linescols["Sols_file_pos"] = pd.to_numeric(file_linescols["Sols_file_pos"], errors="coerce")

def compute_diff(row):
    if pd.isna(row["Sols"]) or pd.isna(row["Sols_file_pos"]):
        return "no_solution"
    else:
        return abs(row["Sols_file_pos"] - row["Sols"])

file_linescols["Invalid solutions"] = file_linescols.apply(compute_diff, axis=1)

# === Save output ===
file_linescols.to_excel("merged_results.xlsx", index=False)
print("✅ Merged results saved to merged_results.xlsx")
