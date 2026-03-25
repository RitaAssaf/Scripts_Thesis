import pandas as pd
import os

classfile_base_path = '/home/etud/Bureau/projet/indicators_pos/run_cspvspolynomial//'

# === Load main Excel file ===
df = pd.read_excel(os.path.join(classfile_base_path, "results.xlsx"))

# === Clean numeric columns ===
df["Wck"] = df["Wck"].astype(str).str.replace(",", ".").astype(float)
df["ilftime"] = pd.to_numeric(df["ilftime"], errors="coerce").fillna(0)

# === Compute total time ===
df["time"] = df["Wck"] + df["ilftime"]

# === Convert ILF column to flag ===
# If ILF column contains 'VRAI'/'FAUX', map them to 1/0
if df["ILF"].dtype == object:
    df["ilf_flag"] = df["ILF"].map({"VRAI": 1, "FAUX": 0}).fillna(0).astype(int)
else:
    df["ilf_flag"] = df["ILF"].astype(int)

# === Group and pivot ===
result = (
    df.groupby(["Target", "Pattern", "ilf_flag"])["time"]
    .mean()
    .unstack(fill_value=0)
    .reset_index()
)

# === Ensure both ILF columns exist ===
for col in [0, 1]:
    if col not in result.columns:
        result[col] = 0

# === Rename columns ===
result = result.rename(columns={0: "time_ilf0", 1: "time_ilf1"})

# === Compute difference ===
result["diff_time"] = result["time_ilf1"] - result["time_ilf0"]

# === Load polynomial timing Excel ===
poly_file = os.path.join("/home/etud/Bureau/projet/indicators_pos/", "run_polynomial_26092025104944/results.xlsx")  # <-- change this filename as needed
poly_df = pd.read_excel(poly_file)

# === Clean and prepare polynomial data ===
poly_df["Time (s)"] = poly_df["Time (s)"].astype(str).str.replace(",", ".").astype(float)

# Keep only relevant columns
poly_df = poly_df[["Pattern", "Target", "Time (s)"]].rename(columns={"Time (s)": "time_polynomial"})

# === Merge polynomial times into result ===
result = pd.merge(result, poly_df, on=["Pattern", "Target"], how="left")

result = result.round(2)

# === Save results ===
output_path = os.path.join(classfile_base_path, "ilf_times_summary.xlsx")
result.to_excel(output_path, index=False)

print(result)
print(df["ILF"].unique())
