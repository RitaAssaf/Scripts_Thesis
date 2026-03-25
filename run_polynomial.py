import subprocess
import os
from datetime import datetime
import time
import openpyxl

# python run_disip.py
patterns = ["pan_apositions-09212025143931", "square_apositions-09212025140420"]
targets=[ "apositions-09222025154923","apositions-09222025154927","apositions-09222025154930","apositions-09222025154933","apositions-09222025154936","apositions-09222025154939","apositions-09222025154946","apositions-09222025154949","apositions-09222025154953","apositions-09222025154957","apositions-09222025155002","apositions-09222025155006","apositions-09222025155009","apositions-09222025155013","apositions-09222025155016","apositions-09222025155022","apositions-09222025155026","apositions-09222025155028","apositions-09222025155030","apositions-09222025155034"]
def write_excel(output_folder, pattern, target, stop, time, matches):
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

	os.makedirs(output_folder, exist_ok=True)
	excel_path = os.path.join(output_folder, f"indicators_{pattern}_{target}_{timestamp}.xlsx")
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Status"
	ws.append(["Pattern", "Target", "Stop", "Time (s)", "Matches"])
	ws.append([pattern, target, stop, time, matches])
	wb.save(excel_path)
	print(f"saved in: {excel_path}")

def run_polynomial_isomorphism(pattern, target):
	cmd = [
		"python", "polynomial_isomorphism.py",
		"--pattern", pattern,
		"--target", target
	]
	start = time.perf_counter()
	result = subprocess.run(cmd, capture_output=True, text=True)
	end = time.perf_counter()

	elapsed = end - start
	print("=== Script Output ===")
	print(result.stdout)
	if result.stderr:
		print("=== Script Errors ===")
		print(result.stderr)
	
	# --- Extract match count from stdout
	match_count = 0
	for line in result.stdout.splitlines():
		if line.startswith("MATCH_COUNT="):
			match_count = int(line.split("=")[1])
			break

	print(f"\n Execution time: {elapsed:.4f} seconds | Matches found: {match_count}")
	return elapsed, match_count


# Create a unique output folder for this run
timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
output_folder = f"/home/etud/Bureau/projet/indicators_pos/run_polynomial_{timestamp}"
os.makedirs(output_folder, exist_ok=True)




for pattern in patterns:
	for target in targets:
		command = [
			"python", "polynomial_isomorphism.py",
			"--pattern", pattern,
			"--target", target,
			"--output", output_folder,
		]

		print(f"Running command: {' '.join(command)}")
		try:
			time_elapsed, match_count = run_polynomial_isomorphism(pattern, target)
			write_excel(output_folder, pattern, target, "COMPLETE", time_elapsed, match_count)

		except subprocess.CalledProcessError as e:
			if e.returncode == -9:
				write_excel(output_folder, pattern, target, "Memory Limit Exceeded", 0, 0)
		except subprocess.TimeoutExpired:
			write_excel(output_folder, pattern, target, "process_timedout", 0, 0)

