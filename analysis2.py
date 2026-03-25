import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the Excel file
file_folder = "/home/etud/Bureau/projet/indicators_pos/run_10092025142625"
file_path=  os.path.join(file_folder, "results.xlsx")

df = pd.read_excel(file_path)

#df['Effs'] = pd.to_numeric(df['Effs'], errors='coerce')
df['Sols'] = pd.to_numeric(df['Sols'], errors='coerce')

selected_patterns = ["pan","gap","net","bowtie","ladder"]
#df = df[df['Pattern'].isin(selected_patterns)]
df = df[df['Pattern']=="pan"]


# Group by 'Pattern' and 'ILF', calculate average 'Effs'
#avg_effs_ilf = df.groupby(['Target', 'ILF'])['Effs'].mean().reset_index()
avg_effs_ilf = df.groupby(['Target', 'ILF'])['Sols'].mean().reset_index()



#avg_effs_ilf = df.groupby(['Pattern', 'ILF'])['Effs'].mean().reset_index()


# Plotting with Seaborn
plt.figure(figsize=(12,6))
sns.barplot(data=avg_effs_ilf, x='Target', y='Sols', hue='ILF', palette='Set2')
#sns.barplot(data=avg_effs_ilf, x='Target', y='Effs', hue='ILF', palette='Set2')

plt.xlabel('Target', fontsize=14)
plt.ylabel('Average Effs', fontsize=14)
plt.title('Average Effective (Effs) by Target with and without ILF', fontsize=14)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

plt.legend(title='ILF', fontsize=12, title_fontsize=13)

plt.tight_layout()
plt.show()
