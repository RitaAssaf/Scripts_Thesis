import pandas as pd

# Load Excel file
# Replace with your actual file path
file_path = "/home/etud/Bureau/projet/fichiers/csp/src/merged_results.xlsx"
out_path = "oom_results.xlsx"

df = pd.read_excel(file_path)

# Normalize the Stop column just in case of extra spaces / case differences
if "Stop" in df.columns:
    df["Stop"] = df["Stop"].astype(str).str.strip()

# Define filters and their conditions
filters = [
    ("Filter_1", {"ILF": False, "Order": False, "Typing": False, "Card": False}),
    ("Filter_2", {"ILF": False, "Order": True,  "Typing": True,  "Card": False}),
    ("Filter_3", {"ILF": True,  "Order": True,  "Typing": True,  "Card": False}),
    ("Filter_4", {"ILF": True,  "Order": True,  "Typing": True,  "Card": True}),
]

# Helper to convert booleans to VRAI/FAUX for the output table
vf = {True: "VRAI", False: "FAUX"}

# Function to compute results (counts + percents)
def compute_stats(filtered: pd.DataFrame) -> dict:
    total = int(len(filtered))
    oom_count = int((filtered["Stop"] == "Memory Limit Exceeded").sum())
    process_timeout = int((filtered["Stop"] == "process_timedout").sum())
    ilf_timeout = int((filtered["Stop"] == "ILF_TIMEOUT").sum())
    solved_instances = int((filtered["Stop"] == "FULL_EXPLORATION").sum())

    pct = lambda n: round((n / total * 100), 2) if total > 0 else 0.0

    other = total - (oom_count + process_timeout + ilf_timeout + solved_instances)

    return {
        "Total Instances": total,
        "OOM Cases": oom_count,
        "Percent OOM": pct(oom_count),
        "Process Timeout Cases": process_timeout,
        "Percent Process Timeout": pct(process_timeout),
        "ILF Timeout Cases": ilf_timeout,
        "Percent ILF Timeout": pct(ilf_timeout),
        "Solved Instances": solved_instances,
        "Percent Solved": pct(solved_instances),
        "Other/Unknown Cases": other,
        "Percent Other/Unknown": pct(other),
    }

rows = []
for name, cond in filters:
    mask = (
        (df["ILF"] == cond["ILF"]) &
        (df["Order"] == cond["Order"]) &
        (df["Typing"] == cond["Typing"]) &
        (df["Card"] == cond["Card"]) 
    )
    stats = compute_stats(df[mask])

    row = {
        "Filter": name,
        "ILF": vf[cond["ILF"]],
        "Order": vf[cond["Order"]],
        "Typing": vf[cond["Typing"]],
        "Card": vf[cond["Card"]],
        **stats,
    }
    rows.append(row)

# Explicit column order to avoid any misalignment in Excel
columns = [
    "Filter", "ILF", "Order", "Typing", "Card",
    "Total Instances",
    "OOM Cases", "Percent OOM",
    "Process Timeout Cases", "Percent Process Timeout",
    "ILF Timeout Cases", "Percent ILF Timeout",
    "Solved Instances", "Percent Solved",
    "Other/Unknown Cases", "Percent Other/Unknown",
]

results_df = pd.DataFrame(rows, columns=columns)

# Write to Excel cleanly
with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
    results_df.to_excel(writer, index=False)

print(f"Aligned results saved to {out_path}")
