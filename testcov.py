import sys
import subprocess

if len(sys.argv) < 2:
    print("Usage: python testcov.py <module>")
    sys.exit(1)

module = sys.argv[1]
cmd = [
    "pytest",
    f"--cov=api/{module}",
    "--cov-report=term-missing",
    "--cov-report=html",
    f"api/{module}/tests/client"
]
subprocess.run(cmd) 