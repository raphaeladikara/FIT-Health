"""Execute the notebook from a clean kernel with cwd pinned to the repo root,
then write both the working copy and the final submission file. Reports any
cell that raised."""
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "notebooks" / "VECTRA_X_Final.ipynb"
SUBMISSION = ROOT / "VECTRA_X_Final_Submission.ipynb"
WORKING = ROOT / "notebooks" / "VECTRA_X_Final.ipynb"

nb = nbformat.read(IN, as_version=4)
client = NotebookClient(
    nb,
    timeout=-1,
    kernel_name="python3",
    resources={"metadata": {"path": str(ROOT)}},
    allow_errors=True,  # run all cells; we inspect errors ourselves
)
t0 = time.time()
client.execute()
dt = time.time() - t0
print(f"executed in {dt:.1f}s")

errors = []
for i, cell in enumerate(nb.cells):
    if cell.get("cell_type") != "code":
        continue
    for out in cell.get("outputs", []):
        if out.get("output_type") == "error":
            errors.append((i, out.get("ename"), out.get("evalue")))

# Persist executed notebook to both targets regardless, for inspection.
nbformat.write(nb, WORKING)
nbformat.write(nb, SUBMISSION)
print("wrote:", WORKING.name, "and", SUBMISSION.name)

if errors:
    print(f"\n!!! {len(errors)} cell(s) errored:")
    for i, en, ev in errors:
        print(f"  cell {i}: {en}: {ev}")
    sys.exit(1)
print("\nALL CELLS EXECUTED WITHOUT ERROR")
