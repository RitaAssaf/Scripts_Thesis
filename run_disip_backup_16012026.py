import subprocess
import os
from datetime import datetime

# python run_disip.py
patterns = ["pan","gap", "net", "bowtie", "pan"]

targets = ["gt-01082026155205","gt-01082026155244","gt-01082026155331","gt-01082026155412","gt-01082026155455","gt-01082026155535","gt-01082026155614","gt-01082026155653","gt-01082026155749","gt-01082026155827","gt-01082026155910","gt-01082026155950","gt-01082026160029","gt-01082026160105","gt-01082026160144","gt-01082026160224","gt-01082026160307","gt-01082026160342","gt-01082026160420","gt-01082026160456"]
common_args_sets = [
	["--ilf"],
	[]
]

# Create a unique output folder for this run
timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
output_folder = f"/home/etud/Bureau/projet/indicators_pos/run_{timestamp}"
#output_folder = f"/home/etud/Bureau/projet/indicators_pos/run_27112025103942"
os.makedirs(output_folder, exist_ok=True)

for pattern in patterns:
	for target in targets:
		for common_args in common_args_sets:
			command = [
				"python", "disip1.py",
				"--pattern", pattern,
				"--target", target,
				"--output", output_folder,
			] + common_args

			print(f"Running command: {' '.join(command)}")
			try:
				subprocess.run(command, check=True)
			except subprocess.CalledProcessError as e:
				print(f"Command failed: {e}")
