import subprocess
import os
from datetime import datetime
import time

#python run_bimodel.py

patterns = ["pan"]

targets=["glc_card_07282025080536"]

pos_patterns = ["pan"]

pos_targets=["gt-07282025080536"]

common_args_sets = [

	["--typage", "--ordre", "--timeout", "--card", "--ilf"],
]

timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
output_folder = f"/home/etud/Bureau/projet/indicators_lines_cols/run_class_b_{timestamp}"
os.makedirs(output_folder, exist_ok=True)

for i in range(1):
		for common_args in common_args_sets:
			command = [
				"python", "bimodel.py",
				"--pattern", patterns[i],
				"--target", targets[i],
				"--output", output_folder,  
				"--pos_pattern", pos_patterns[i],
				"--pos_target", pos_targets[i],
			] + common_args

			print(f"Running command: {' '.join(command)}")
			try:
				subprocess.run(command, check=True, timeout= 3600)
				time.sleep(2)
			except subprocess.CalledProcessError as e:
				print(f"Command failed: {e}")
