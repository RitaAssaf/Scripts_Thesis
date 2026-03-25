import pandas as pd
import os
classfile_base_path='/home/etud/Bureau/projet/indicators_pos/run_02102025153519/'

subcomponents_paths='/home/etud/Bureau/projet/fichiers/csp/src/logs/'
# Load files
results = pd.read_excel(os.path.join(classfile_base_path, "results.xlsx"))
subs = pd.read_excel(os.path.join(subcomponents_paths,"subcomponents_20251002_132617.xlsx"))
parent_results = pd.read_excel(os.path.join('/home/etud/Bureau/projet/indicators_pos/run_10092025134853/', "results.xlsx")  )# your parent table

# === Clean numeric columns ===
results["Effs"] = pd.to_numeric(results["Effs"].astype(str).str.replace("-", ""), errors="coerce")
parent_results["Effs"] = pd.to_numeric(parent_results["Effs"].astype(str).str.replace("-", ""), errors="coerce")

# Rename Effs column in parent_results so it's consistent
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
comparison.to_excel("effs_parent_vs_subs.xlsx", index=False)

print("✅ File 'effs_parent_vs_subs.xlsx' generated in current folder with columns:")
print(list(comparison.columns))
