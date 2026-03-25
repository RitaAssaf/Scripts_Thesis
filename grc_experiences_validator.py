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

def check_targets_per_patterns(directory, patterns, targets, expected_per_pattern=1):
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



def check_results_bimodel(directory, patterns, targets, pos_targets, expected_per_pattern=1):
	file_path = os.path.join(directory, "results.xlsx")

	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"'results.xlsx' not found in {directory}")

	expected_total = len(patterns) * expected_per_pattern

	#create a dictionnary of pos and lc targets:
	dict_lc_pos={targets[i]: pos_targets[i] for i in range(len(targets))}

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
		pos_targets =[dict_lc_pos[lc_target] for lc_target in targets ]
		pos_targets_line = ",".join(f'"{t}"' for t in pos_targets)
		print(
			f"\nTargets with missing pattern(s) [{patterns_line}]:\n"
			f"{targets_line}\n"
			f"Position graphs:\n"
			f"{pos_targets_line}"
		)


	return target_pattern_counts



def read_last_file3_name(excel_path, col_name='file3_name'):
	# Read the Excel file
	df = pd.read_excel(excel_path)

	# Ensure the column exists
	if col_name not in df.columns:
		raise ValueError(f"Column {col_name} not found in the Excel file")

	# Get the last non-null value in the column
	last_value = df[col_name].dropna().iloc[-1]

	return last_value



if __name__ == "__main__":
	directory_path = "/home/etud/Bureau/projet/indicators_pos/run_23032026141936/"
	targets_path = "/home/etud/Bureau/projet/fichiers/csp/generated_files_db/class_b_28072025080534.xlsx"
	lc_targets_string =read_last_file3_name(targets_path, "file4_name")
	pos_targets_string =read_last_file3_name(targets_path, "file5_name")

	lc_targets= [item.strip('"') for item in lc_targets_string.split(',')]
	pos_targets = [item.strip('"') for item in pos_targets_string.split(',')]
	pattern_names = [ "pan","gap","net","bowtie","ladder"]
	check_results_bimodel(directory_path, pattern_names, lc_targets,pos_targets,1)