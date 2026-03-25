import argparse

import subprocess
import os
from datetime import datetime
import time
import signal
import re
import openpyxl

import resource

# python run_bimodel_param.py --output "/home/etud/Bureau/projet/indicators_pos/run_12032026144957/" --patterns  --pos_targets --rc_targets 


MAX_MEM_GB = 20
MAX_MEM_BYTES = MAX_MEM_GB * 1024**3  



def limit_memory():
	soft, hard = resource.getrlimit(resource.RLIMIT_AS)
	# Only lower the soft limit; do not try to raise hard limit
	new_soft = min(MAX_MEM_BYTES, hard)
	resource.setrlimit(resource.RLIMIT_AS, (new_soft, hard))


def run_bimodel(patterns,pos_targets, rc_targets, folder):
	common_args_sets = [
	]
	TIMEOUT_SECONDS=3600

	for pattern in patterns:
		for i in range(len(pos_targets)):
				command = [
					"python", "bimodel.py",
				"--pattern", pattern,
				"--target", str(rc_targets[i]),
				"--output", folder,  
				"--pos_pattern", pattern,
				"--pos_target", str(pos_targets[i]),
				]

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
	parser.add_argument("--pos_targets", type=str, help="targets as comma-separated strings")
	parser.add_argument("--rc_targets", type=str, help="targets as comma-separated strings")

	parser.add_argument("--output", type=str, help="output folder", default=default_folder)

	args = parser.parse_args()
	print(args)
	patterns = args.patterns.split(",") if args.patterns else []
	pos_targets = args.pos_targets.split(",") if args.pos_targets else []
	rc_targets = args.rc_targets.split(",") if args.rc_targets else []

	folder = args.output
	os.makedirs(folder, exist_ok=True)


	run_bimodel(patterns,pos_targets,rc_targets, folder)