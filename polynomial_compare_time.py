import pandas as pd
import os

classfile_base_path='/home/etud/Bureau/projet/indicators_pos/run_23092025154227/'

# === Load Excel file ===
df = pd.read_excel((os.path.join(classfile_base_path,"results24092025095048.xlsx")))

# === Clean numeric columns ===
# Replace commas with dots and convert to float
df["Wck"] = df["Wck"].astype(str).str.replace(",", ".").astype(float)
df["ilftime"] = pd.to_numeric(df["ilftime"], errors="coerce").fillna(0)

# === Compute total time ===
df["time"] = df["Wck"] + df["ilftime"]

# === Extract ILF flag (1 or 0) ===
# If you have a column that indicates ILF=1 or ILF=0, you can use it directly.
# But from your example, "ILF" is a column with values "VRAI" (True) and "FAUX" (False),
# so we can map it:
df["ilf_flag"] = df["ILF"].astype(int)

# === Group by Target and Pattern ===
# Then pivot to get time for ilf=1 and ilf=0 side by side
# === Group and pivot ===
result = (
    df.groupby(["Target", "Pattern", "ilf_flag"])["time"]
    .mean()
    .unstack(fill_value=0)
    .reset_index()
)

# === Ensure both columns (0 and 1) exist ===
if 0 not in result.columns:
    result[0] = 0
if 1 not in result.columns:
    result[1] = 0

# === Rename columns ===
result = result.rename(columns={0: "time_ilf0", 1: "time_ilf1"})

# === Compute difference ===
result["diff_time"] = result["time_ilf1"] - result["time_ilf0"]


# === Save results ===
result.to_excel("ilf_times_summary.xlsx", index=False)

print(result)
print(df["ILF"].unique())
 