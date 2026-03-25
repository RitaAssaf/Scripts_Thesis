import pandas as pd
import os

#subcomponents results folder path
classfile_base_path='/home/etud/Bureau/projet/indicators_lines_cols/run_class_200x50_08102025134822/'
#mapping between subs and parents file path
subcomponents_paths='/home/etud/Bureau/projet/fichiers/csp/src/logs/'
# resultss on subcomponents
results = pd.read_excel(os.path.join(classfile_base_path, "results.xlsx"))
#mapping between parent and sub
subs = pd.read_excel(os.path.join(subcomponents_paths,"subcomponents_20251002_132617.xlsx"))
#results for parent graph without partition
parent_results = pd.read_excel(os.path.join('/home/etud/Bureau/projet/indicators_pos/run_10092025134853/', "results.xlsx")  )# your parent table

# === Clean numeric columns ===
results["Effs"] = pd.to_numeric(results["Effs"].astype(str).str.replace("-", ""), errors="coerce")
parent_results["Effs"] = pd.to_numeric(parent_results["Effs"].astype(str).str.replace("-", ""), errors="coerce")

parent_results = parent_results.rename(columns={"Effs": "Effs_parent"})


# === Merge subcomponents with results ===
merged = subs.merge(results, left_on="Subcomponent", right_on="Target", how="left")

# === Compute sum Effs by Pattern, ILF, Parent Graph ===
sum_by_parent = (
    merged.groupby(["Pattern", "ILF", "Parent Graph"], dropna=False)["Effs"]
    .sum()
    .reset_index()
    .rename(columns={"Effs": "Effs_subsum"})
)

for df in [parent_results, sum_by_parent]:
    for col in ["Pattern", "ILF", "Target"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
# === Merge with parent-level results ===
comparison = parent_results.merge(
    sum_by_parent,
    left_on=["Pattern", "Target", "ILF"],
    right_on=["Pattern", "Parent Graph", "ILF"],
    suffixes=("_parent", "_subsum"),
    how="left"
)

# === Ensure numeric before subtraction ===
comparison["Effs_parent"] = pd.to_numeric(comparison["Effs_parent"], errors="coerce")
comparison["Effs_subsum"] = pd.to_numeric(comparison["Effs_subsum"], errors="coerce")

# === Compute Difference ===
comparison["Difference"] = comparison["Effs_parent"] - comparison["Effs_subsum"]

# === Reorder and keep only requested columns ===
final_cols = [
    "Parent Graph", "Pattern", "Target", "ILF",
    "Effs_parent", "Effs_subsum", "Difference"
]

comparison = comparison[final_cols]

# === Save final Excel file ===
comparison.to_excel(os.path.join(classfile_base_path,"effs_parent_vs_subs.xlsx"), index=False)

print(f" File 'effs_parent_vs_subs.xlsx' generated in {classfile_base_path}")
print(list(comparison.columns))
