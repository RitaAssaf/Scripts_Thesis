import argparse

import subprocess
import os
from datetime import datetime
import time
import signal
import re
import openpyxl

import resource

# python run_disip_param.py --patterns  --targets --output "/home/etud/Bureau/projet/indicators_pos/run_17012026122712"


MAX_MEM_GB = 20
MAX_MEM_BYTES = MAX_MEM_GB * 1024**3  



def limit_memory():
	soft, hard = resource.getrlimit(resource.RLIMIT_AS)
	# Only lower the soft limit; do not try to raise hard limit
	new_soft = min(MAX_MEM_BYTES, hard)
	resource.setrlimit(resource.RLIMIT_AS, (new_soft, hard))


def run_disip(patterns,targets, folder):
	common_args_sets = [
		["--ilf"],
		[]
	]
	TIMEOUT_SECONDS=10800

	for pattern in patterns:
		for target in targets:
			for common_args in common_args_sets:
				command = [
					"python", "disip.py",
					"--pattern", pattern,
					"--target", target,
					"--output", folder,
				] + common_args

				print(f"Running command: {' '.join(command)}")
				try:
					subprocess.run(command, check=True, timeout=TIMEOUT_SECONDS,preexec_fn=limit_memory)
				except subprocess.CalledProcessError as e:
					print(f"Command failed: {e}")

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Batch-run generateur.py")
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
	default_folder = f"/home/etud/Bureau/projet/indicators_pos/run_{timestamp}"

	parser.add_argument("--patterns", type=str, help="patterns as comma-separated strings")
	parser.add_argument("--targets", type=str, help="targets as comma-separated strings")
	parser.add_argument("--output", type=str, help="output folder", default=default_folder)

	args = parser.parse_args()

	patterns = args.patterns.split(",") if args.patterns else []
	targets = args.targets.split(",") if args.targets else []
	folder = args.output
	os.makedirs(folder, exist_ok=True)


	run_disip(patterns,targets, folder)