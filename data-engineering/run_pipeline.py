import subprocess
import sys


def run_step(command, name):
    print()
    print("=" * 50)
    print(name)
    print("=" * 50)

    result = subprocess.run(
        [sys.executable, command],
        check=False
    )

    if result.returncode != 0:
        print(f"{name} FAILED")
        sys.exit(result.returncode)

    print(f"{name} COMPLETED")


# Step 1: Fetch fresh USGS data
run_step("ingestion_usgs.py", "USGS INGESTION")

# Step 2: Process all reports
run_step("ingestion.py", "DATA PROCESSING")

# Step 3: Validate AI input
run_step("test_ai_input.py", "AI INPUT VALIDATION")

print()
print("=" * 50)
print("DISASTERLENS PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 50)