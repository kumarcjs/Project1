"""
run_tests.py
============
Runs every generated test script in --dir, collects results,
and produces a rich HTML report with:
  • Top summary: Total / Pass / Fail counts
  • Per test case: result badge, step table (only FAILED steps shown)
  • Failures include actual vs expected + comment

Usage:
    python run_tests.py --dir generated_tests
    python run_tests.py --dir generated_tests --out reports/test_report.html
"""

import os, sys, json, importlib.util, argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--dir", default="generated_tests")
parser.add_argument("--out", default="reports/test_report.html")
args = parser.parse_args()

os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
NOW = datetime.now().strftime("%d %b %Y — %H:%M:%S")

# ── Run all scripts ───────────────────────────────────────────
results = []
scripts = sorted(f for f in os.listdir(args.dir) if f.endswith(".py"))

print(f"\n🚀 Running {len(scripts)} test scripts...\n")
for fname in scripts:
    fpath = os.path.join(args.dir, fname)
    spec  = importlib.util.spec_from_file_location("tc_module", fpath)
    mod   = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        result = mod.run()
        results.append(result)
        status = "PASS ✅" if result["passed"] else "FAIL ❌"
        print(f"  {status}  {result['tc_id']} — {result['tc_name']}  "
              f"({result['passed_steps']}/{result['total_steps']} steps)")
    except Exception as e:
        print(f"  💥 ERROR  {fname}: {e}")
        results.append({
            "tc_id": fname.replace(".py",""), "tc_name": fname,
            "passed": False, "total_steps": 0,
            "passed_steps": 0, "failed_steps": 1,
            "steps": [{"label": "Script load/run error", "op": "—",
                        "passed": False, "comment": str(e),
                        "actual": None, "expected": None, "tol": None}],
        })

# ── Summary counts ────────────────────────────────────────────
total_tc  = len(results)
pass_tc   = sum(1 for r in results if r["passed"])
fail_tc   = total_tc - pass_tc
total_st  = sum(r["total_steps"]  for r in results)
pass_st   = sum(r["passed_steps"] for r in results)
fail_st   = sum(r["failed_steps"] for r in results)
pass_rate = int(pass_tc / total_tc * 100) if total_tc else 0

# ── HTML builders ─────────────────────────────────────────────
PHASE_COLORS = {
    "PRECONDITION":  ("#DBEAFE","#1D4ED8","🔵"),
    "ACTION":        ("#D1FAE5","#065F46","🟢"),
    "POSTCONDITION": ("#FFE4E6","#9F1239","🔴"),
}

def phase_of(label):
    l = label.upper()
    if "PRECONDITION" in l: return "PRECONDITION"
    if "ACTION"       in l: return "ACTION"
    if "POSTCONDITION" in l: return "POSTCONDITION"
    return "ACTION"

def step_table(steps):
    failed = [s for s in steps if not s["passed"]]
    if not failed:
        return ""   # no failed steps — nothing to render
    rows = ""
    for s in failed:
        ph = phase_of(s["label"])
        bg, col, icon = PHASE_COLORS.get(ph, ("#F9FAFB","#374151","⚪"))
        act = f"{s['actual']}" if s["actual"] is not None else "—"
        exp = f"{s['expected']}" if s["expected"] is not None else "—"
        tol = f"±{s['tol']}"   if s["tol"]      is not None else "—"
        rows += f"""
        <tr>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9">
            <span style="background:{bg};color:{col};font-size:10px;font-weight:700;
                  padding:2px 8px;border-radius:12px">{icon} {ph}</span>
          </td>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;
                font-size:12px;color:#334155">{s['label']}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;
                text-align:center">
            <span style="font-family:monospace;font-size:11px;
                  background:#F1F5F9;padding:2px 8px;border-radius:4px;
                  color:#0EA5E9">{s['op']}</span>
          </td>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;
                font-family:monospace;font-size:12px;color:#0EA5E9;
                text-align:center">{exp}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;
                font-family:monospace;font-size:12px;color:#EF4444;
                font-weight:700;text-align:center">{act}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;
                font-family:monospace;font-size:11px;color:#6B7280;
                text-align:center">{tol}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #F1F5F9;
                font-size:11px;color:#DC2626">{s['comment']}</td>
        </tr>"""
    return f"""
    <div style="margin-top:14px;border-radius:8px;overflow:hidden;
         border:1px solid #FCA5A5">
      <div style="background:#FEF2F2;padding:8px 14px;font-size:11px;
           font-weight:700;color:#991B1B;letter-spacing:.5px;
           border-bottom:1px solid #FCA5A5">
        ❌ FAILED STEPS ({len(failed)})
      </div>
      <table style="width:100%;border-collapse:collapse;background:white">
        <thead>
          <tr style="background:#FFF7F7">
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:left;letter-spacing:.8px">PHASE</th>
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:left;letter-spacing:.8px">STEP</th>
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:center;letter-spacing:.8px">OP</th>
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:center;letter-spacing:.8px">EXPECTED</th>
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:center;letter-spacing:.8px">ACTUAL</th>
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:center;letter-spacing:.8px">TOLERANCE</th>
            <th style="padding:8px 12px;font-size:10px;color:#9CA3AF;
                font-weight:700;text-align:left;letter-spacing:.8px">COMMENT</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""

def tc_card(r):
    ok       = r["passed"]
    tc_id    = r["tc_id"]
    tc_name  = r["tc_name"]
    total_s  = r["total_steps"]
    pass_s   = r["passed_steps"]
    fail_s   = r["failed_steps"]
    pct      = int(pass_s / total_s * 100) if total_s else 0

    result_badge = (
        '<span style="background:#DCFCE7;color:#166534;font-size:11px;'
        'font-weight:800;padding:4px 14px;border-radius:20px;'
        'letter-spacing:.5px">✅ PASS</span>'
        if ok else
        '<span style="background:#FEE2E2;color:#991B1B;font-size:11px;'
        'font-weight:800;padding:4px 14px;border-radius:20px;'
        'letter-spacing:.5px">❌ FAIL</span>'
    )

    bar_color = "#10B981" if ok else "#EF4444"
    left_border = "#10B981" if ok else "#EF4444"
    steps_html = step_table(r.get("steps", []))

    # Mini step pills (all steps, color by pass/fail)
    pills = ""
    for i, s in enumerate(r.get("steps", []), 1):
        col   = "#10B981" if s["passed"] else "#EF4444"
        bg    = "#DCFCE7" if s["passed"] else "#FEE2E2"
        tip   = s["label"].replace(chr(34), "&quot;")
        pills += ("<span title=" + chr(34) + tip + chr(34)
                  + " style=display:inline-flex;align-items:center;justify-content:center;"
                  + "width:22px;height:22px;border-radius:50%;font-size:9px;font-weight:700;"
                  + f"background:{bg};color:{col};margin:2px>{i}</span>")

    return f"""
  <div style="background:white;border-radius:12px;border:1px solid #E2E8F0;
       border-left:4px solid {left_border};margin-bottom:16px;
       box-shadow:0 1px 4px rgba(0,0,0,.06);overflow:hidden">

    <!-- Card header -->
    <div style="padding:16px 20px;display:flex;align-items:center;
         justify-content:space-between;gap:16px;flex-wrap:wrap;
         border-bottom:{'' if not steps_html else '1px solid #FEE2E2'}">
      <div style="display:flex;align-items:center;gap:14px">
        {result_badge}
        <div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:13px;
               font-weight:700;color:#0F172A">{tc_id}</div>
          <div style="font-size:12px;color:#64748B;margin-top:1px">{tc_name}</div>
        </div>
      </div>

      <div style="display:flex;align-items:center;gap:20px">
        <!-- step pills -->
        <div style="display:flex;flex-wrap:wrap;gap:0;max-width:260px">{pills}</div>

        <!-- mini stats -->
        <div style="display:flex;gap:12px">
          <div style="text-align:center">
            <div style="font-size:16px;font-weight:800;color:#10B981">{pass_s}</div>
            <div style="font-size:9px;color:#9CA3AF;font-weight:600">PASS</div>
          </div>
          <div style="text-align:center">
            <div style="font-size:16px;font-weight:800;color:#EF4444">{fail_s}</div>
            <div style="font-size:9px;color:#9CA3AF;font-weight:600">FAIL</div>
          </div>
          <div style="text-align:center">
            <div style="font-size:16px;font-weight:800;color:#64748B">{total_s}</div>
            <div style="font-size:9px;color:#9CA3AF;font-weight:600">TOTAL</div>
          </div>
        </div>

        <!-- progress bar -->
        <div style="width:100px">
          <div style="display:flex;justify-content:space-between;
               font-size:10px;color:#94A3B8;margin-bottom:4px">
            <span>Steps</span><span style="font-weight:700;color:{bar_color}">{pct}%</span>
          </div>
          <div style="height:6px;background:#F1F5F9;border-radius:3px;overflow:hidden">
            <div style="width:{pct}%;height:100%;background:{bar_color};
                 border-radius:3px"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Failed steps table (only if failures exist) -->
    {"<div style='padding:0 20px 16px'>" + steps_html + "</div>" if steps_html else ""}
  </div>"""

all_cards = "\n".join(tc_card(r) for r in results)

# ── Donut SVG ─────────────────────────────────────────────────
def donut_svg(passed, total, size=120):
    if total == 0: return ""
    r = 46; cx = cy = size // 2
    circ = 2 * 3.14159 * r
    pct = passed / total
    p_arc = circ * pct
    f_arc = circ * (1 - pct)
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
              stroke="#FEE2E2" stroke-width="14"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
              stroke="#10B981" stroke-width="14"
              stroke-dasharray="{p_arc:.1f} {f_arc:.1f}"
              stroke-dashoffset="{circ/4:.1f}"
              stroke-linecap="round"/>
      <text x="{cx}" y="{cy-6}" text-anchor="middle"
            font-family="'Syne',sans-serif" font-size="18" font-weight="800"
            fill="#0F172A">{pass_tc}</text>
      <text x="{cx}" y="{cy+12}" text-anchor="middle"
            font-family="Arial" font-size="9" fill="#94A3B8">PASSED</text>
    </svg>"""

svg = donut_svg(pass_tc, total_tc)

# ── Phase legend for header ───────────────────────────────────
phase_legend = "".join(
    f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;'
    f'color:#64748B;margin-right:16px">'
    f'<span style="width:8px;height:8px;border-radius:50%;background:{col}"></span>'
    f'{icon} {ph.title()}</span>'
    for ph, (bg, col, icon) in PHASE_COLORS.items()
)

# ── Full HTML ─────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{("✅ ALL PASS" if fail_tc==0 else f"❌ {fail_tc} FAILED")} — dSPACE HIL Test Report</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'DM Sans',sans-serif;background:#F1F5F9;color:#1E293B;min-height:100vh}}

  /* ── Hero ── */
  .hero{{
    background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);
    padding:40px 52px 0;
    position:relative;overflow:hidden;
  }}
  .hero::after{{
    content:'';position:absolute;inset:0;
    background:
      radial-gradient(ellipse at 15% 60%,rgba(16,185,129,.12) 0%,transparent 55%),
      radial-gradient(ellipse at 85% 30%,rgba(239,68,68,.10) 0%,transparent 50%);
    pointer-events:none;
  }}
  .hero-grid{{
    position:absolute;inset:0;
    background-image:
      linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),
      linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
    background-size:44px 44px;
  }}
  .hero-inner{{position:relative;z-index:1}}

  /* top row */
  .hero-top{{
    display:flex;align-items:flex-start;
    justify-content:space-between;gap:32px;
    flex-wrap:wrap;margin-bottom:36px;
  }}
  .badge-strip{{
    display:flex;align-items:center;gap:8px;margin-bottom:12px;
  }}
  .badge{{
    font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;
    padding:4px 11px;border-radius:20px;
  }}
  .badge-hil{{background:rgba(14,165,233,.15);color:#38BDF8;border:1px solid rgba(14,165,233,.25)}}
  .badge-time{{background:rgba(255,255,255,.07);color:#94A3B8;border:1px solid rgba(255,255,255,.1)}}
  h1{{
    font-family:'Syne',sans-serif;font-size:clamp(22px,2.8vw,32px);
    font-weight:800;color:#F8FAFC;line-height:1.1;letter-spacing:-.5px;
    margin-bottom:6px;
  }}
  h1 em{{color:#34D399;font-style:normal}}
  .hero-sub{{font-size:12px;color:#64748B;font-weight:300}}

  /* summary card */
  .summary-card{{
    background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
    border-radius:14px;padding:20px 28px;
    display:flex;align-items:center;gap:28px;
  }}
  .s-stat{{text-align:center;min-width:70px}}
  .s-num{{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;line-height:1}}
  .s-lbl{{font-size:10px;color:#64748B;font-weight:600;text-transform:uppercase;
          letter-spacing:1px;margin-top:3px}}
  .divider{{width:1px;height:60px;background:rgba(255,255,255,.1)}}

  /* stat strip */
  .stat-strip{{
    display:flex;border-top:1px solid rgba(255,255,255,.07);
    margin-top:36px;position:relative;z-index:1;
  }}
  .ss-item{{
    flex:1;padding:16px 20px;text-align:center;
    border-right:1px solid rgba(255,255,255,.06);
    transition:background .2s;
  }}
  .ss-item:last-child{{border-right:none}}
  .ss-item:hover{{background:rgba(255,255,255,.04)}}
  .ss-num{{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;line-height:1;margin-bottom:3px}}
  .ss-lbl{{font-size:9px;color:#4B5563;text-transform:uppercase;letter-spacing:1px;font-weight:600}}

  /* main */
  .main{{padding:28px 52px 52px;max-width:1300px}}

  /* filter */
  .toolbar{{
    display:flex;align-items:center;gap:8px;
    margin-bottom:18px;flex-wrap:wrap;
  }}
  .f-btn{{
    padding:6px 16px;border-radius:20px;border:1.5px solid #E2E8F0;
    background:white;font-size:11px;font-weight:600;color:#64748B;
    cursor:pointer;transition:all .18s;font-family:'DM Sans',sans-serif;
  }}
  .f-btn:hover,.f-btn.on{{background:#0F172A;border-color:#0F172A;color:white}}

  @media(max-width:800px){{
    .hero,.main{{padding:20px}}
    .summary-card{{flex-wrap:wrap}}
  }}
</style>
</head>
<body>

<!-- ═══ HERO ═══════════════════════════════════════════════ -->
<div class="hero">
  <div class="hero-grid"></div>
  <div class="hero-inner">
    <div class="hero-top">

      <!-- Left: title -->
      <div>
        <div class="badge-strip">
          <span class="badge badge-hil">dSPACE AutomationDesk · HIL</span>
          <span class="badge badge-time">🕐 {NOW}</span>
        </div>
        <h1>Test Execution <em>Report</em></h1>
        <p class="hero-sub">Step-level tracking · CAN · LIN · MAPort · UDS/OBD</p>
        <div style="margin-top:16px">{phase_legend}</div>
      </div>

      <!-- Right: summary card -->
      <div class="summary-card">
        {svg}
        <div class="divider"></div>
        <div class="s-stat">
          <div class="s-num" style="color:#F8FAFC">{total_tc}</div>
          <div class="s-lbl">Total TCs</div>
        </div>
        <div class="divider"></div>
        <div class="s-stat">
          <div class="s-num" style="color:#34D399">{pass_tc}</div>
          <div class="s-lbl">Passed</div>
        </div>
        <div class="divider"></div>
        <div class="s-stat">
          <div class="s-num" style="color:#F87171">{fail_tc}</div>
          <div class="s-lbl">Failed</div>
        </div>
        <div class="divider"></div>
        <div class="s-stat">
          <div class="s-num" style="color:#60A5FA">{pass_rate}%</div>
          <div class="s-lbl">Pass Rate</div>
        </div>
      </div>
    </div>
  </div>

  <!-- step-level strip -->
  <div class="stat-strip">
    <div class="ss-item">
      <div class="ss-num" style="color:#C084FC">{total_st}</div>
      <div class="ss-lbl">Total Steps</div>
    </div>
    <div class="ss-item">
      <div class="ss-num" style="color:#34D399">{pass_st}</div>
      <div class="ss-lbl">Steps Passed</div>
    </div>
    <div class="ss-item">
      <div class="ss-num" style="color:#F87171">{fail_st}</div>
      <div class="ss-lbl">Steps Failed</div>
    </div>
    <div class="ss-item">
      <div class="ss-num" style="color:#38BDF8">{int(pass_st/total_st*100) if total_st else 0}%</div>
      <div class="ss-lbl">Step Pass Rate</div>
    </div>
    <div class="ss-item">
      <div class="ss-num" style="color:#94A3B8">{len(scripts)}</div>
      <div class="ss-lbl">Scripts Run</div>
    </div>
  </div>
</div>

<!-- ═══ MAIN ════════════════════════════════════════════════ -->
<div class="main">

  <div class="toolbar">
    <button class="f-btn on" onclick="filterTC('all',this)">All ({total_tc})</button>
    <button class="f-btn" onclick="filterTC('pass',this)">✅ Passed ({pass_tc})</button>
    <button class="f-btn" onclick="filterTC('fail',this)">❌ Failed ({fail_tc})</button>
  </div>

  <div id="cards">
    {all_cards}
  </div>

  <div style="margin-top:36px;padding-top:18px;border-top:1px solid #E2E8F0;
       font-size:11px;color:#CBD5E1;text-align:center">
    dSPACE AutomationDesk HIL Framework &nbsp;·&nbsp;
    Test Report &nbsp;·&nbsp; {NOW} &nbsp;·&nbsp;
    {total_tc} Test Cases &nbsp;·&nbsp; {total_st} Steps &nbsp;·&nbsp;
    Pass Rate {pass_rate}%
  </div>
</div>

<script>
function filterTC(mode, btn) {{
  document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('#cards > div').forEach(card => {{
    const hasFail = card.querySelector('[style*="FAILED STEPS"]');
    if (mode === 'all') card.style.display = '';
    else if (mode === 'pass') card.style.display = hasFail ? 'none' : '';
    else card.style.display = hasFail ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""

with open(args.out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n{'='*55}")
print(f"  TEST RESULTS: {pass_tc}/{total_tc} PASSED  ({pass_rate}% pass rate)")
print(f"  STEPS: {pass_st}/{total_st} passed, {fail_st} failed")
print(f"  REPORT → {args.out}")
print(f"{'='*55}\n")
