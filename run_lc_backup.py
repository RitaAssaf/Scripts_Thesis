import subprocess
import os
from datetime import datetime

# Define your parameters here
patterns = ["pan"]
targets = ["glc_card_07282025080535"]
common_args = [ "--ilf","--typage", "--ordre", "--card"]

# Create a unique output folder for this run
timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
output_folder = f"/home/etud/Bureau/projet/indicators_lines_cols/run_{timestamp}"
os.makedirs(output_folder, exist_ok=True)

for pattern in patterns:
	for target in targets:
		command = [
			"python", "lc6.py",
			"--pattern", pattern,
			"--target", target,
			"--output", output_folder,  # Pass folder to lc4.py
		] + common_args

		print(f"Running command: {' '.join(command)}")
		try:
			subprocess.run(command, check=True, timeout=7200)
			time.sleep(2)
		except subprocess.CalledProcessError as e:
			print(f"Command failed: {e}")
