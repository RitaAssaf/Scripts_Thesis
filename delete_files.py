import sys
from pathlib import Path

BASE_DIR = Path("/home/etud/Bureau/projet/fichiers/csp/lcres")

def delete_files(names):
	for name in names:
		filename = f"{name}.dot"
		file_path = BASE_DIR / filename

		if file_path.exists():
			try:
				file_path.unlink()
				print(f"Deleted: {file_path}")
			except Exception as e:
				print(f"Error deleting {file_path}: {e}")
		else:
			print(f"File not found: {file_path}")

def main():
	if len(sys.argv) < 2:
		print("Usage: python delete_lcres_files.py <file1> <file2> ...")
		sys.exit(1)

	filenames = sys.argv[1:]
	delete_files(filenames)

if __name__ == "__main__":
	main()