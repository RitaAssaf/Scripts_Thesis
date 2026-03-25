import pandas as pd
import os

# === File paths ===
general = "/home/etud/Bureau/projet/indicators_lines_cols/"

child_run_file = os.path.join(general, "run_class_200x50_08102025134822/results.xlsx")
parent_run_file = os.path.join(general, "run_class_b_09092025100441/results.xlsx")
subcomponents_file = os.path.join("/home/etud/Bureau/projet/fichiers/csp/src/logs/", "subcomponents_20251002_132617.xlsx")
output_excel = os.path.join(general, "compare_efficiency_summary.xlsx")

# === Read Excel files ===
def read_any(path):
    try:
        return pd.read_excel(path)
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        raise

child_df = read_any(child_run_file)
parent_df = read_any(parent_run_file)
sub_df = read_any(subcomponents_file)

# === Normalize column names ===
child_df.columns = child_df.columns.str.strip()
parent_df.columns = parent_df.columns.str.strip()
sub_df.columns = sub_df.columns.str.strip()

# === Build mapping of child -> parent ===
mapping = sub_df[["Parent Graph", "glc_card"]].drop_duplicates()
mapping.rename(columns={"Parent Graph": "ParentTarget", "glc_card": "ChildTarget"}, inplace=True)

# === Merge child run data with mapping ===
child_with_parent = child_df.merge(
    mapping, how="left", left_on="Target", right_on="ChildTarget"
)

# Drop rows without parent mapping
child_with_parent = child_with_parent.dropna(subset=["ParentTarget"])

# Convert Effs columns to numeric
child_with_parent["Effs"] = pd.to_numeric(child_with_parent["Effs"], errors="coerce")
parent_df["Effs"] = pd.to_numeric(parent_df["Effs"], errors="coerce")

# === Aggregate child effs by (Pattern, ParentTarget) ===
child_sum = (
    child_with_parent.groupby(["Pattern", "ParentTarget"], as_index=False)["Effs"]
    .sum()
    .rename(columns={"Effs": "SumChildEffs"})
)

# === Prepare parent effs data ===
parent_eff = parent_df[["Pattern", "Target", "Effs"]].rename(
    columns={"Target": "ParentTarget", "Effs": "ParentEffs"}
)

# === Merge comparisons ===
compare_df = child_sum.merge(parent_eff, on=["Pattern", "ParentTarget"], how="outer")

# === Compute difference ===
compare_df["Diff(ChildSum-Parent)"] = compare_df["SumChildEffs"] - compare_df["ParentEffs"]

# === Export results to Excel ===
with pd.ExcelWriter(output_excel) as writer:
    compare_df.to_excel(writer, sheet_name="Comparison", index=False)
    child_with_parent.to_excel(writer, sheet_name="ChildDetails", index=False)
    parent_eff.to_excel(writer, sheet_name="ParentEffs", index=False)

print(f"✅ Comparison Excel generated successfully at:\n{output_excel}")
