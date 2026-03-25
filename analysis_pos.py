import pandas as pd
import os

# Load the Excel file
file_folder = "/home/etud/Bureau/projet/indicators_pos/run_27112025103942"
file_path=  os.path.join(file_folder, "results.xlsx")

df = pd.read_excel(file_path)

# Ensure numeric conversion for columns of interest
for col in ['Effs', 'Wrgs', 'ilftime']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Group by 'Pattern' and 'ILF' to calculate averages
avg_values = (
    df.groupby([ 'ILF'])
    [['Effs', 'Wrgs', 'ilftime']]
    .mean()
    .reset_index()
)

# Save to Excel
output_path=  os.path.join(file_folder, "avg_results.xlsx")
avg_values.to_excel(output_path, index=False)

print(f"Average results saved to: {output_path}")
print(avg_values)
