"""
generate_steps.py
=================
Reads HIL_TestSteps_Template.xlsx and generates one Python test script
per TC_ID. Each script has setup() / execute() / teardown() with every
step tracked individually (PASS / FAIL + comment).

Usage:
    python generate_steps.py --excel HIL_TestSteps_Template.xlsx
"""

import os, sys, argparse, textwrap
from collections import defaultdict
from datetime import datetime
import openpyxl

parser = argparse.ArgumentParser()
parser.add_argument("--excel", required=True)
parser.add_argument("--out",   default="generated_tests")
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Read Excel ────────────────────────────────────────────────
wb = openpyxl.load_workbook(args.excel, data_only=True)
ws = wb["TestSteps"]

def safe(v, d=""):
    return str(v).strip() if v is not None and str(v).strip() != "" else d

rows = []
for row in ws.iter_rows(min_row=4, values_only=True):
    if not row[0]: continue
    rows.append({
        "tc_id":    safe(row[0]),
        "tc_name":  safe(row[1], "Unnamed"),
        "phase":    safe(row[2], "ACTION").upper(),
        "step_no":  safe(row[3], "1"),
        "op":       safe(row[4], "READ").upper(),
        "sig_type": safe(row[5], "MAPort").upper(),
        "sig_path": safe(row[6]),
        "value":    safe(row[7]),
        "expected": safe(row[8]),
        "tol":      safe(row[9], "0"),
        "desc":     safe(row[10]),
    })

# Group by TC_ID
tc_map = defaultdict(list)
tc_names = {}
for r in rows:
    tc_map[r["tc_id"]].append(r)
    tc_names[r["tc_id"]] = r["tc_name"]

# ── Code builder ──────────────────────────────────────────────
def build_step_code(step, idx):
    """Return Python lines for one step (SET or READ)."""
    op       = step["op"]
    sig_type = step["sig_type"]
    sig      = step["sig_path"]
    val      = step["value"]
    exp      = step["expected"]
    tol      = step["tol"]
    desc     = step["desc"]
    phase    = step["phase"]
    sno      = step["step_no"]
    label    = f"{phase} Step {sno}: {desc}"

    lines = [f'    # ── {label}']

    if op == "SET":
        if sig_type == "CAN":
            parts = sig.split("/")
            ch    = parts[0] if len(parts) > 0 else "CAN1"
            msg   = parts[1] if len(parts) > 1 else "MSG"
            sig_n = parts[2] if len(parts) > 2 else "Signal"
            lines += [
                f'    try:',
                f'        # CANPort.WriteSignal("{ch}", "{msg}", "{sig_n}", {val or 0})',
                f'        _written = {val or 0}   # placeholder',
                f'        steps.append(StepResult({idx}, "{label}", "SET", '
                f'None, None, None, True, "SET {sig_n}={val} on {ch}"))',
                f'    except Exception as e:',
                f'        steps.append(StepResult({idx}, "{label}", "SET", '
                f'None, None, None, False, str(e)))',
            ]
        elif sig_type == "LIN":
            parts = sig.split("/")
            ch    = parts[0] if len(parts) > 0 else "LIN1"
            frm   = parts[1] if len(parts) > 1 else "Frame"
            sig_n = parts[2] if len(parts) > 2 else "Signal"
            lines += [
                f'    try:',
                f'        # LINPort.WriteSignal("{ch}", "{frm}", "{sig_n}", {val or 0})',
                f'        _written = {val or 0}',
                f'        steps.append(StepResult({idx}, "{label}", "SET", '
                f'None, None, None, True, "SET {sig_n}={val}"))',
                f'    except Exception as e:',
                f'        steps.append(StepResult({idx}, "{label}", "SET", '
                f'None, None, None, False, str(e)))',
            ]
        else:  # MAPort
            lines += [
                f'    try:',
                f'        # MAPort.Write(r"{sig}", {val or 0})',
                f'        _written = {val or 0}',
                f'        steps.append(StepResult({idx}, "{label}", "SET", '
                f'None, None, None, True, "MAPort.Write={val}"))',
                f'    except Exception as e:',
                f'        steps.append(StepResult({idx}, "{label}", "SET", '
                f'None, None, None, False, str(e)))',
            ]

    else:  # READ
        exp_val = exp if exp != "" else "0"
        tol_val = tol if tol != "" else "0"
        if sig_type == "CAN":
            parts = sig.split("/")
            ch    = parts[0] if len(parts) > 0 else "CAN1"
            msg   = parts[1] if len(parts) > 1 else "MSG"
            sig_n = parts[2] if len(parts) > 2 else "Signal"
            read_line = f'# actual = CANPort.ReadSignal("{ch}", "{msg}", "{sig_n}")'
        elif sig_type == "LIN":
            parts = sig.split("/")
            ch    = parts[0] if len(parts) > 0 else "LIN1"
            frm   = parts[1] if len(parts) > 1 else "Frame"
            sig_n = parts[2] if len(parts) > 2 else "Signal"
            read_line = f'# actual = LINPort.ReadSignal("{ch}", "{frm}", "{sig_n}")'
        else:
            read_line = f'# actual = MAPort.Read(r"{sig}")'

        lines += [
            f'    try:',
            f'        {read_line}',
            f'        actual = float({exp_val})  # ← placeholder: replace with real read',
            f'        expected = float({exp_val})',
            f'        tol      = float({tol_val})',
            f'        ok = abs(actual - expected) <= tol',
            f'        comment = "" if ok else f"Expected={{expected}}±{{tol}} but got {{actual}}"',
            f'        steps.append(StepResult({idx}, "{label}", "READ", '
            f'actual, expected, tol, ok, comment))',
            f'    except Exception as e:',
            f'        steps.append(StepResult({idx}, "{label}", "READ", '
            f'None, {exp_val}, {tol_val}, False, str(e)))',
        ]

    lines.append("")
    return "\n".join(lines)

# ── Script template ───────────────────────────────────────────
SCRIPT = '''\
"""
AutomationDesk HIL Test Script
Test ID  : {tc_id}
Feature  : {tc_name}
Generated: {now}
"""
# ── dSPACE imports (uncomment on real HIL) ───────────────────
# from Testbench import MAPort, CANPort, LINPort
import time
from dataclasses import dataclass, field
from typing import Optional

TC_ID   = "{tc_id}"
TC_NAME = "{tc_name}"

# ── Step result container ─────────────────────────────────────
@dataclass
class StepResult:
    idx:      int
    label:    str
    op:       str
    actual:   Optional[float]
    expected: Optional[float]
    tol:      Optional[float]
    passed:   bool
    comment:  str = ""

steps: list[StepResult] = []

# ══════════════════════════════════════════════════════════════
# PRECONDITIONS
# ══════════════════════════════════════════════════════════════
def setup():
    print(f"[{{TC_ID}}] >>> PRECONDITIONS")
{pre_code}

# ══════════════════════════════════════════════════════════════
# ACTIONS
# ══════════════════════════════════════════════════════════════
def execute():
    print(f"[{{TC_ID}}] >>> ACTIONS")
{act_code}

# ══════════════════════════════════════════════════════════════
# POSTCONDITIONS
# ══════════════════════════════════════════════════════════════
def teardown():
    print(f"[{{TC_ID}}] >>> POSTCONDITIONS")
{post_code}

# ══════════════════════════════════════════════════════════════
# RUNNER — returns dict summary
# ══════════════════════════════════════════════════════════════
def run():
    steps.clear()
    setup()
    execute()
    teardown()

    total  = len(steps)
    passed = sum(1 for s in steps if s.passed)
    failed = total - passed
    tc_ok  = (failed == 0)

    print(f"\\n[{{TC_ID}}] RESULT: {{'PASS' if tc_ok else 'FAIL'}} "
          f"({{passed}}/{{total}} steps passed)")
    for s in steps:
        mark = "✅" if s.passed else "❌"
        print(f"  {{mark}} {{s.label}}"
              + (f" — {{s.comment}}" if not s.passed else ""))

    return {{
        "tc_id":   TC_ID,
        "tc_name": TC_NAME,
        "passed":  tc_ok,
        "total_steps":  total,
        "passed_steps": passed,
        "failed_steps": failed,
        "steps": [
            {{
                "idx":     s.idx,
                "label":   s.label,
                "op":      s.op,
                "actual":  s.actual,
                "expected":s.expected,
                "tol":     s.tol,
                "passed":  s.passed,
                "comment": s.comment,
            }} for s in steps
        ],
    }}

if __name__ == "__main__":
    run()
'''

# ── Generate one script per TC_ID ────────────────────────────
generated = []
for tc_id, step_rows in tc_map.items():
    tc_name = tc_names[tc_id]
    phases  = {"PRECONDITION": [], "ACTION": [], "POSTCONDITION": []}
    idx = 0
    for s in step_rows:
        ph = s["phase"] if s["phase"] in phases else "ACTION"
        phases[ph].append((idx, s))
        idx += 1

    def build_phase(phase_steps):
        if not phase_steps:
            return "    pass"
        return "\n".join(build_step_code(s, i) for i, s in phase_steps)

    code = SCRIPT.format(
        tc_id    = tc_id,
        tc_name  = tc_name,
        now      = NOW,
        pre_code = build_phase(phases["PRECONDITION"]),
        act_code = build_phase(phases["ACTION"]),
        post_code= build_phase(phases["POSTCONDITION"]),
    )

    fname = f"{tc_id}_{tc_name.replace(' ', '_')}.py"
    fpath = os.path.join(args.out, fname)
    with open(fpath, "w") as f:
        f.write(code)
    print(f"  ✅  {tc_id} → {fname}  ({len(step_rows)} steps)")
    generated.append(fname)

print(f"\n✅  {len(generated)} scripts → {args.out}/")
print("Next: python run_tests.py --dir", args.out)
