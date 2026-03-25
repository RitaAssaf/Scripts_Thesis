import os
import pandas as pd
from collections import defaultdict

def check_pattern_in_excel(directory, pattern, expected_count=40):
	file_path = os.path.join(directory, "results.xlsx")

	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"'results.xlsx' not found in {directory}")

	total_count = 0

	excel_file = pd.ExcelFile(file_path)
	for sheet_name in excel_file.sheet_names:
		df = excel_file.parse(sheet_name, dtype=str)

		total_count += df.apply(
			lambda col: col.fillna("").str.count(pattern)
		).sum().sum()

	print(f"Pattern '{pattern}' found {total_count} times.")

	if total_count == expected_count:
		print("✅ Pattern appears exactly 40 times.")
		return True
	else:
		print("❌ Pattern does NOT appear 40 times.")
		return False

def check_targets_per_patterns(directory, patterns, targets, expected_per_pattern=2):
	# for pattern_name in pattern_names:
	# 	check_pattern_in_excel(directory_path, pattern_name)

	file_path = os.path.join(directory, "results.xlsx")

	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"'results.xlsx' not found in {directory}")

	# Expected total = patterns × expected_per_pattern
	expected_total = len(patterns) * expected_per_pattern

	# Initialize counters
	target_counts = {target: 0 for target in targets}

	excel_file = pd.ExcelFile(file_path)

	for sheet_name in excel_file.sheet_names:
		df = excel_file.parse(sheet_name, dtype=str).fillna("")

		for pattern in patterns:
			for target in targets:
				# Count cells containing BOTH pattern and target
				count = df.apply(
					lambda col: col.str.contains(pattern) & col.str.contains(target)
				).sum().sum()

				target_counts[target] += count

	print("\n===== TARGET VERIFICATION REPORT =====")

	for target, count in target_counts.items():
		if count == expected_total:
			print(f"✅ Target '{target}' appears exactly {expected_total} times.")
		elif count < expected_total:
			missing = expected_total - count
			print(f"❌ Target '{target}' is MISSING {missing} occurrences "
				  f"({count}/{expected_total}).")
		else:
			extra = count - expected_total
			print(f"⚠️ Target '{target}' appears {extra} times TOO MANY "
				  f"({count}/{expected_total}).")

	return target_counts

def check_targets_per_patterns_1(directory, patterns, targets, expected_per_pattern=2):
	file_path = os.path.join(directory, "results.xlsx")

	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"'results.xlsx' not found in {directory}")

	expected_total = len(patterns) * expected_per_pattern

	# target -> pattern -> count
	target_pattern_counts = {
		target: {pattern: 0 for pattern in patterns}
		for target in targets
	}

	excel_file = pd.ExcelFile(file_path)

	for sheet_name in excel_file.sheet_names:
		df = excel_file.parse(sheet_name, dtype=str).fillna("")

		for pattern in patterns:
			for target in targets:
				count = df[
					(df["Pattern"] == pattern) &
					(df["Target"] == target)
				].shape[0]
				target_pattern_counts[target][pattern] += count

	print("\n===== TARGET / PATTERN VERIFICATION REPORT =====")

	for target, pattern_counts in target_pattern_counts.items():
		total_count = sum(pattern_counts.values())

		if total_count == expected_total:
			print(f"✅ Target '{target}' appears exactly {expected_total} times.")
			continue

		# Identify missing or excess patterns
		missing_patterns = [
			p for p, c in pattern_counts.items() if c < expected_per_pattern
		]

		excess_patterns = [
			p for p, c in pattern_counts.items() if c > expected_per_pattern
		]

		if total_count < expected_total:
			missing = expected_total - total_count
			print(
				f"❌ Target '{target}' is MISSING {missing} occurrences "
				f"({total_count}/{expected_total}). "
				f"Missing pattern(s): {', '.join(missing_patterns)}"
			)

		else:
			extra = total_count - expected_total
			print(
				f"⚠️ Target '{target}' appears {extra} times TOO MANY "
				f"({total_count}/{expected_total}). "
				f"Excess pattern(s): {', '.join(excess_patterns)}"
			)


	# --- GROUP TARGETS WITH SAME MISSING PATTERNS ---
	grouped_missing = defaultdict(list)

	for target, pattern_counts in target_pattern_counts.items():
		missing_patterns = tuple(
			sorted(p for p, c in pattern_counts.items() if c < expected_per_pattern)
		)

		if missing_patterns:
			grouped_missing[missing_patterns].append(target)

	# --- PRINT TARGETS IN SINGLE-LINE FORMAT ---
	for missing_patterns, targets in grouped_missing.items():
		targets_line = ",".join(f'"{t}"' for t in targets)
		patterns_line = ",".join(f'"{t}"' for t in missing_patterns)

		print(
			f"\nTargets with missing pattern(s) [{patterns_line}]:\n"
			f"{targets_line}"
		)


	return target_pattern_counts



def count_net_sols_zero(directory,pattern_0_sols, sheet_name=0):
	file_path = os.path.join(directory, "results.xlsx")

	# Load Excel file
	df = pd.read_excel(file_path, sheet_name=sheet_name)

	# Filter rows
	filtered = df[(df["Pattern"] == pattern_0_sols) & (df["Sols"] == 0) & (df["ILF"] == False)]

	return len(filtered)


def read_last_file4_name(excel_path):
	# Read the Excel file
	df = pd.read_excel(excel_path)

	# Ensure the column exists
	if 'file4_name' not in df.columns:
		raise ValueError("Column 'file4_name' not found in the Excel file")

	# Get the last non-null value in the column
	last_value = df['file4_name'].dropna().iloc[-1]

	return last_value





if __name__ == "__main__":
	directory_path = "/home/etud/Bureau/projet/indicators_pos/run_10092025142625/" #class 40
	#directory_path = "/home/etud/Bureau/projet/indicators_pos/run_17012026122712/"
	targets_path = "/home/etud/Bureau/projet/fichiers/csp/generated_files_db/file_17012026114406.xlsx"
	targets_string =read_last_file4_name(targets_path)
	targets= [item.strip('"') for item in targets_string.split(',')]
	pattern_names = ["ladder","gap", "bowtie", "net","pan"]
	#targets=["gt-01082026155205","gt-01082026155244","gt-01082026155331","gt-01082026155412","gt-01082026155455","gt-01082026155535","gt-01082026155614","gt-01082026155653","gt-01082026155749","gt-01082026155827","gt-01082026155910","gt-01082026155950","gt-01082026160029","gt-01082026160105","gt-01082026160144","gt-01082026160224","gt-01082026160307","gt-01082026160342","gt-01082026160420","gt-01082026160456"]
	#check_targets_per_patterns_1(directory_path, pattern_names, targets)
	pattern_0_sols='net'
	count = count_net_sols_zero(directory_path,pattern_0_sols)
	print(f"Number of targets with Pattern='{pattern_0_sols}' and Sols=0: {count}")