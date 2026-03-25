import shutil
from pathlib import Path
import argparse
from datetime import datetime

#python merge_folders.py     --path /home/etud/Bureau/projet/indicators_lines_cols/     --folders 

def merge_folders(folder_list, base_path, output_folder):
	"""
	Merge files from multiple folders into one folder.

	Args:
		folder_list (list[str]): List of folder names to merge.
		base_path (str): Base directory containing the folders.
	"""
	output_path = Path(output_folder)
	output_path.mkdir(parents=True, exist_ok=True)

	for folder_name in folder_list:
		folder_path = Path(base_path) / folder_name
		if not folder_path.is_dir():
			print(f"Skipping {folder_path} (not a directory)")
			continue
		
		for file in folder_path.iterdir():
			if file.is_file():
				destination = output_path / file.name
				
				# Handle name collisions
				counter = 1
				while destination.exists():
					destination = output_path / f"{file.stem}_{counter}{file.suffix}"
					counter += 1
				
				shutil.copy2(file, destination)
				#print(f"Copied {file} → {destination}")

	print(f" All files copied to: {output_path.resolve()}")

if __name__ == "__main__":
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

	parser = argparse.ArgumentParser(description="Merge files from multiple folders into one folder.")
	parser.add_argument("--path", required=True, help="Base path containing the folders.")
	parser.add_argument("--folders", nargs="+", required=True, help="List of folder names to merge (space-separated).")

	args = parser.parse_args()

	merge_folders(args.folders, args.path, f"{args.path}/merged_folder_{timestamp}")
