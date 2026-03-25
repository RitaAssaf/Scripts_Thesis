import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Organize each sheet in Excel by the "Pattern" column.')
parser.add_argument('--file', type=str, required=True, help='Name of the file (without .xlsx extension)')
parser.add_argument('--folder', type=str, required=True, help='Name of the folder')

args = parser.parse_args()
file = args.file
folder = args.folder

# Input and output file paths
file_path = f"/home/etud/Bureau/projet/{folder}/{file}.xlsx"
#output_file = f"/home/etud/Bureau/projet/{folder}/grouped_by_pattern.xlsx"

# Load the Excel file
#file_path = "grouped_by_pattern.xlsx"  # Update this path as needed
xls = pd.ExcelFile(file_path)

# Load the target sheet
df = xls.parse('bipartite_transitivity')

# Define the desired boolean order
desired_order = [
    ("FAUX", "FAUX", "FAUX", "FAUX"),
    ("FAUX", "VRAI", "VRAI", "VRAI"),
    ("VRAI", "VRAI", "VRAI", "VRAI"),
    ("VRAI", "VRAI", "VRAI", "FAUX")
]

# Helper function to rank each row based on boolean combination
def get_order_rank(row):
    key = (row["ilf"], row["typage"], row["ordre"], row["card"])
    return desired_order.index(key) if key in desired_order else len(desired_order)

# Apply ranking and sort
df["order_rank"] = df.apply(get_order_rank, axis=1)
df_sorted = df.sort_values(by=["Pattern", "order_rank"]).drop(columns="order_rank")

# Optionally save to a new Excel file
df_sorted.to_excel(f"/home/etud/Bureau/projet/{folder}/sorted_bipartite_transitivity.xlsx", index=False)

print( f"Sheet has been sorted and saved to /home/etud/Bureau/projet/{folder}/sorted_bipartite_transitivity.xlsx")
