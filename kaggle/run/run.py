"""Kaggle launcher: clone Witness Networks at a pinned commit, install vLLM, run the pipeline.
Edit COMMIT / ARGS, then push with tools/kaggle_cli.py kernels push -p kaggle/run."""
import subprocess, sys
COMMIT = "__COMMIT__"
ARGS = "__ARGS__"
def sh(c):
    print("+", c, flush=True)
    subprocess.run(c, shell=True, check=True)
sh("git clone -q https://github.com/ShreySharma07/witness-network /kaggle/working/wn_src")
sh(f"cd /kaggle/working/wn_src && git checkout -q {COMMIT}")
sh(f"{sys.executable} -m pip install -q vllm")
sh(f"cd /kaggle/working/wn_src && {sys.executable} scripts/pipeline.py --backend vllm --out /kaggle/working/out {ARGS}")
