import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_charts(file_folder,x_value,y_value, for_a_given_pattern='',title=''):
	# Load the Excel file
	file_path=  os.path.join(file_folder, "results.xlsx")

	df = pd.read_excel(file_path)

	#df['Effs'] = pd.to_numeric(df['Effs'], errors='coerce')
	df[y_value] = pd.to_numeric(df[y_value], errors='coerce')

	selected_patterns = ["pan","gap","net","bowtie","ladder"]
	if for_a_given_pattern!= '':
		df = df[df['Pattern']==for_a_given_pattern]
	else:
		df = df[df['Pattern'].isin(selected_patterns)]



	# Group by 'Pattern' and 'ILF', calculate average 'Effs'
	#avg_effs_ilf = df.groupby(['Target', 'ILF'])['Effs'].mean().reset_index()
	avg_effs_ilf = df.groupby([x_value])[y_value].mean().reset_index()

	# Plotting with Seaborn
	plt.figure(figsize=(12,6))
	sns.barplot(data=avg_effs_ilf, x=x_value, y=y_value, hue=x_value,  palette='Set2')
	#sns.barplot(data=avg_effs_ilf, x='Target', y='Effs', hue='ILF', palette='Set2')

	plt.xlabel(x_value, fontsize=14)
	plt.ylabel(y_value, fontsize=14)
	plt.title(title, fontsize=14)
	plt.xticks(rotation=45, fontsize=14)
	plt.yticks(fontsize=14)

	plt.tight_layout()
	plt.show()

if __name__ == '__main__':
	
	file_folder = "/home/etud/Bureau/projet/indicators_pos/run_10092025142625"
	plot_charts(file_folder,'Target','Sols','net')