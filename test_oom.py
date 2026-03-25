import psutil
import threading
import subprocess
import time
from datetime import datetime
import sys

def monitor_and_kill(pid, threshold_gb=0.001, interval=1):
    """Monitor process (and children) memory and kill if exceeds threshold."""
    try:
        parent = psutil.Process(pid)
        while parent.is_running():
            mem_used_gb = parent.memory_info().rss / (1024 ** 3)
            for child in parent.children(recursive=True):
                mem_used_gb += child.memory_info().rss / (1024 ** 3)

            if mem_used_gb > threshold_gb:
                print(f"[WARNING] Memory exceeded {threshold_gb} GB ({mem_used_gb:.4f} GB). Killing process...")
                with open("memory_log.txt", "a") as log_file:
                    log_file.write(f"[{datetime.now()}] Killed process due to memory limit ({mem_used_gb:.4f} GB)\n")

                for child in parent.children(recursive=True):
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                parent.terminate()
                try:
                    parent.wait(timeout=5)
                except psutil.TimeoutExpired:
                    parent.kill()
                break

            time.sleep(interval)
    except psutil.NoSuchProcess:
        pass

if __name__ == "__main__":
    # Launch a dummy Python process that consumes memory
    command = [sys.executable, "-c",
               "data = []; "
               "import time; "
               "[data.append(bytearray(1024*1024)) or time.sleep(0.1) for _ in range(10)]"]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    monitor_thread = threading.Thread(target=monitor_and_kill, args=(process.pid, 0.001), daemon=True)
    monitor_thread.start()

    stdout, stderr = process.communicate()

    print("Process finished.")
    if stdout:
        print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)
