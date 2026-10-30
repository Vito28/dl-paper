import sys, os, time, json
from pathlib import Path
import nbformat
from nbclient import NotebookClient
os.environ["HR_SMOKE"] = "1"
d = Path(sys.argv[1]); only = sys.argv[2:]
for p in sorted(d.glob("*.ipynb")):
    if only and not any(p.name.startswith(o) for o in only): continue
    nb = nbformat.read(p, as_version=4)
    t0 = time.time()
    try:
        NotebookClient(nb, timeout=1200, kernel_name="python3", resources={"metadata": {"path": str(d)}}).execute()
        print(f"OK   {p.name} ({time.time()-t0:.0f}s)")
    except Exception as e:
        print(f"FAIL {p.name}\n{str(e)[-3000:]}"); sys.exit(1)
