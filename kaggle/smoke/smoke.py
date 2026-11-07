"""Witness Networks GPU smoke test: install vLLM, load an open 7B model, measure throughput and JSON compliance."""
import json, subprocess, sys, time

R = {}
t0 = time.time()
R["nvidia_smi"] = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], capture_output=True, text=True).stdout
print(R["nvidia_smi"], flush=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "vllm"], check=True)
R["install_s"] = round(time.time() - t0, 1)
print("installed", R["install_s"], flush=True)

import torch
from vllm import LLM, SamplingParams
n_gpu = torch.cuda.device_count()
R["n_gpu"] = n_gpu
MODEL = "Qwen/Qwen2.5-7B-Instruct-AWQ"
t1 = time.time()
llm = LLM(model=MODEL, quantization="awq", dtype="half", tensor_parallel_size=1,
          max_model_len=8192, gpu_memory_utilization=0.90, enforce_eager=False)
R["model"] = MODEL
R["load_s"] = round(time.time() - t1, 1)
print("loaded", R["load_s"], flush=True)

SYS = ("You are agent {i} in an 8-agent team fixing a data pipeline. Reply ONLY with JSON: "
       '{{"thought": str, "messages": [{{"to": int, "body": str}}], "tool": {{"name": str, "args": dict}} or null}}')
prompts = []
for i in range(64):
    msgs = [{"role": "system", "content": SYS.format(i=i % 8)},
            {"role": "user", "content": f"Round {i//8}. Teammate {(i+1)%8} says: 'validator fails on null dates'. Your module: transform. Decide your next action."}]
    prompts.append(msgs)
sp = SamplingParams(temperature=0.7, max_tokens=300, seed=0)
t2 = time.time()
outs = llm.chat(prompts, sp)
dt = time.time() - t2
gen_tokens = sum(len(o.outputs[0].token_ids) for o in outs)
ok = 0
for o in outs:
    txt = o.outputs[0].text.strip().strip("`")
    if txt.startswith("json"):
        txt = txt[4:]
    try:
        json.loads(txt); ok += 1
    except Exception:
        pass
R.update(batch=64, batch_s=round(dt, 1), gen_tokens=gen_tokens, tok_per_s=round(gen_tokens / dt, 1),
         json_ok_rate=ok / 64, sample=outs[0].outputs[0].text[:600], total_s=round(time.time() - t0, 1))
print(json.dumps(R, indent=2), flush=True)
json.dump(R, open("/kaggle/working/smoke.json", "w"), indent=2)
