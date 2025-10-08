import subprocess
from pathlib import Path

B_USER = "d300"
B_HOST = "miu-nix-office" 
REMOTE_DIR = "/home/d300/TEMP" 
FILENAMES = ["test1.py", "test2.py"] 
LOCAL_DIR = "/home/miu7898/coding/test/t1" 

Path(LOCAL_DIR).mkdir(parents=True, exist_ok=True)

sources = [f"{B_USER}@{B_HOST}:{REMOTE_DIR.rstrip('/')}/{name}" for name in FILENAMES]

cmd = [
    "scp",
    *sources,
    LOCAL_DIR,
]

res = subprocess.run(
    cmd,
    check=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    timeout=60,
)

print(res.stdout or "Done.")

