import subprocess

def is_heap_size_valid(heap_gb):
    command = ["java", f"-Xmx{heap_gb}g", "-version"]
    try:
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        stderr = process.stderr.lower()
        # Check error message in stderr
        if "could not reserve enough space" in stderr:
            return False
        return process.returncode == 0
    except Exception as e:
        print(f"Error testing heap size {heap_gb}g: {e}")
        return False

# Test heap sizes 1 to 12 GB
for size in range(1, 13):
    if is_heap_size_valid(size):
        print(f"Heap size {size}GB is valid")
    else:
        print(f"Heap size {size}GB is NOT valid")
