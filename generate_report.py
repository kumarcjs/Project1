"""
dSPACE AutomationDesk — Script Report Generator
================================================
Scans generated_tests/ folder, parses every .py script,
and produces a rich interactive HTML report.

Usage:
    python generate_report.py
    python generate_report.py --dir generated_tests --out reports/script_report.html
"""

import os, re, argparse, json
from datetime import datetime

# ── CLI ───────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--dir", default="generated_tests", help="Folder with generated scripts")
parser.add_argument("--out", default="reports/script_report.html", help="Output HTML path")
args = parser.parse_args()

SCRIPTS_DIR = args.dir
OUT_PATH    = args.out
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
NOW         = datetime.now().strftime("%d %b %Y, %H:%M")

# ── Parser: extract metadata from script ─────────────────────
def parse_script(filepath):
    with open(filepath, "r") as f:
        src = f.read()

    def get(pattern, default="—"):
        m = re.search(pattern, src)
        return m.group(1).strip() if m else default

    # Determine type from docstring
    if "CAN Bus" in src:       typ = "CAN"
    elif "LIN Bus" in src:     typ = "LIN"
    elif "MAPort" in src and "Diagnostics" not in src: typ = "MODEL VAR"
    elif "Diagnostics" in src: typ = "DIAGNOSTICS"
    else:                      typ = "UNKNOWN"

    # Count uncommented vs commented dSPACE API calls
    api_calls   = re.findall(r'^\s*#.*(?:MAPort|CANPort|LINPort|DiagPort)\.\w+', src, re.M)
    active_calls= re.findall(r'^\s*(?!#).*(?:MAPort|CANPort|LINPort|DiagPort)\.\w+', src, re.M)
    total_api   = len(api_calls) + len(active_calls)
    activated   = len(active_calls)
    pct         = int((activated / total_api * 100) if total_api else 0)

    # Count lines
    lines = src.strip().split("\n")
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]

    # Check which sections exist
    has_setup    = "def setup"    in src
    has_execute  = "def execute"  in src
    has_verify   = "def verify"   in src
    has_teardown = "def teardown" in src

    return {
        "filename":    os.path.basename(filepath),
        "test_id":     get(r'TEST_ID\s*=\s*["\']([^"\']+)'),
        "feature":     get(r'Feature\s*:\s*(.+)'),
        "type":        typ,
        "generated":   get(r'Generated:\s*(.+)'),
        "total_lines": len(lines),
        "code_lines":  len(code_lines),
        "api_total":   total_api,
        "api_active":  activated,
        "api_pct":     pct,
        "has_setup":   has_setup,
        "has_execute": has_execute,
        "has_verify":  has_verify,
        "has_teardown":has_teardown,
        "steps_ok":    sum([has_setup, has_execute, has_verify, has_teardown]),
        # Protocol-specific fields
        "channel":     get(r'CHANNEL\s*=\s*["\']([^"\']+)'),
        "signal":      get(r'SIGNAL\s*=\s*["\']([^"\']+)'),
        "expected":    get(r'EXPECTED\s*=\s*([^\n#]+)'),
        "tolerance":   get(r'TOLERANCE\s*=\s*([^\n#]+)'),
        "wait_time":   get(r'WAIT_TIME\s*=\s*([^\n#]+)'),
        "precondition":get(r'PRECONDITION\s*=\s*["\']([^"\']+)'),
        "service_id":  get(r'SERVICE_ID\s*=\s*["\']([^"\']+)'),
        "protocol":    get(r'PROTOCOL\s*=\s*["\']([^"\']+)'),
        "source":      src,
    }

# ── Load all scripts ──────────────────────────────────────────
files = sorted(f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py"))
scripts = []
for fname in files:
    try:
        data = parse_script(os.path.join(SCRIPTS_DIR, fname))
        scripts.append(data)
        print(f"  ✅  Parsed: {fname}")
    except Exception as e:
        print(f"  ❌  Error parsing {fname}: {e}")

# ── Stats ─────────────────────────────────────────────────────
total      = len(scripts)
by_type    = {}
for s in scripts:
    by_type[s["type"]] = by_type.get(s["type"], 0) + 1
fully_impl = sum(1 for s in scripts if s["api_pct"] == 100)
partial    = sum(1 for s in scripts if 0 < s["api_pct"] < 100)
template   = sum(1 for s in scripts if s["api_pct"] == 0)
total_lines= sum(s["total_lines"] for s in scripts)

# ── Type colours & icons ──────────────────────────────────────
TYPE_META = {
    "CAN":        {"color": "#0EA5E9", "bg": "#E0F2FE", "icon": "⚡"},
    "LIN":        {"color": "#8B5CF6", "bg": "#EDE9FE", "icon": "〰️"},
    "MODEL VAR":  {"color": "#10B981", "bg": "#D1FAE5", "icon": "📐"},
    "DIAGNOSTICS":{"color": "#F59E0B", "bg": "#FEF3C7", "icon": "🔍"},
    "UNKNOWN":    {"color": "#6B7280", "bg": "#F3F4F6", "icon": "❓"},
}

def type_badge(t):
    m = TYPE_META.get(t, TYPE_META["UNKNOWN"])
    return (f'<span style="background:{m["bg"]};color:{m["color"]};'
            f'font-size:10px;font-weight:700;padding:3px 9px;border-radius:20px;'
            f'letter-spacing:.5px;white-space:nowrap">{m["icon"]} {t}</span>')

def step_chip(label, ok):
    if ok:
        return (f'<span style="background:#DCFCE7;color:#166534;font-size:10px;'
                f'padding:2px 7px;border-radius:12px;font-weight:600">{label} ✓</span>')
    return (f'<span style="background:#F3F4F6;color:#9CA3AF;font-size:10px;'
            f'padding:2px 7px;border-radius:12px">{label}</span>')

def api_bar(pct):
    if pct == 0:   color, label = "#94A3B8", "Template"
    elif pct < 100: color, label = "#F59E0B", f"{pct}% Active"
    else:           color, label = "#10B981", "Full HIL"
    return f'''<div style="display:flex;align-items:center;gap:8px">
      <div style="flex:1;height:6px;background:#E5E7EB;border-radius:3px;overflow:hidden">
        <div style="width:{pct}%;height:100%;background:{color};border-radius:3px;
             transition:width .6s ease"></div>
      </div>
      <span style="font-size:10px;color:{color};font-weight:700;white-space:nowrap">{label}</span>
    </div>'''

# ── Build script cards ────────────────────────────────────────
def extra_row(s):
    t = s["type"]
    if t == "CAN":
        return f"Ch: <b>{s['channel']}</b> &nbsp;|&nbsp; Signal: <b>{s['signal']}</b>"
    if t == "LIN":
        return f"Ch: <b>{s['channel']}</b> &nbsp;|&nbsp; Signal: <b>{s['signal']}</b>"
    if t == "MODEL VAR":
        return f"Expected: <b>{s['expected']}</b> &nbsp;|&nbsp; Tol: <b>{s['tolerance']}</b>"
    if t == "DIAGNOSTICS":
        return f"Proto: <b>{s['protocol']}</b> &nbsp;|&nbsp; SID: <b>{s['service_id']}</b>"
    return ""

def escape_html(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def script_row(s, idx):
    m    = TYPE_META.get(s["type"], TYPE_META["UNKNOWN"])
    extr = extra_row(s)
    code_escaped = escape_html(s["source"])
    return f"""
    <tr class="script-row" onclick="toggleCode('{idx}')">
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9">
        <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
             font-weight:700;color:#1E293B">{s['test_id']}</div>
        <div style="font-size:10px;color:#94A3B8;margin-top:2px">{s['filename']}</div>
      </td>
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9">
        <div style="font-size:13px;color:#334155;font-weight:500">{s['feature']}</div>
        <div style="font-size:10px;color:#94A3B8;margin-top:3px">{extr}</div>
      </td>
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9;text-align:center">
        {type_badge(s['type'])}
      </td>
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9">
        <div style="display:flex;gap:4px;flex-wrap:wrap">
          {step_chip("SETUP",    s['has_setup'])}
          {step_chip("EXEC",     s['has_execute'])}
          {step_chip("VERIFY",   s['has_verify'])}
          {step_chip("TEARDOWN", s['has_teardown'])}
        </div>
      </td>
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9;min-width:140px">
        {api_bar(s['api_pct'])}
      </td>
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9;text-align:center">
        <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
              color:#64748B">{s['total_lines']}L</span>
      </td>
      <td style="padding:12px 16px;border-bottom:1px solid #F1F5F9;text-align:center">
        <div style="width:28px;height:28px;border-radius:50%;border:1.5px solid #CBD5E1;
             display:flex;align-items:center;justify-content:center;
             font-size:11px;color:#94A3B8;margin:auto;transition:all .2s"
             class="expand-btn" id="btn-{idx}">▾</div>
      </td>
    </tr>
    <tr id="code-{idx}" style="display:none">
      <td colspan="7" style="padding:0;border-bottom:2px solid {m['color']}">
        <div style="background:#0F172A;margin:0">
          <div style="padding:8px 16px;background:#1E293B;display:flex;
               align-items:center;justify-content:between;gap:12px">
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                  color:{m['color']};font-weight:700">{s['filename']}</span>
            <span style="font-size:10px;color:#64748B;margin-left:auto">
              {s['total_lines']} lines &nbsp;·&nbsp; {s['code_lines']} code lines
            </span>
          </div>
          <pre style="margin:0;padding:16px;overflow-x:auto;font-family:'JetBrains Mono',
               monospace;font-size:11.5px;line-height:1.7;color:#E2E8F0;
               max-height:420px;overflow-y:auto"><code>{code_escaped}</code></pre>
        </div>
      </td>
    </tr>"""

all_rows = "\n".join(script_row(s, i) for i, s in enumerate(scripts))

# ── Donut chart data ──────────────────────────────────────────
type_colors = {"CAN":"#0EA5E9","LIN":"#8B5CF6","MODEL VAR":"#10B981","DIAGNOSTICS":"#F59E0B","UNKNOWN":"#6B7280"}
donut_segments = []
start = 0
for typ, cnt in by_type.items():
    pct = cnt / total * 100
    color = type_colors.get(typ, "#6B7280")
    donut_segments.append(f'<div style="position:absolute;inset:0" '
                          f'data-type="{typ}" data-pct="{pct:.1f}" data-color="{color}"></div>')

type_legend = ""
for typ, cnt in by_type.items():
    col = type_colors.get(typ, "#6B7280")
    m   = TYPE_META.get(typ, TYPE_META["UNKNOWN"])
    type_legend += f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
      <div style="width:10px;height:10px;border-radius:50%;background:{col};flex-shrink:0"></div>
      <span style="font-size:12px;color:#64748B">{m['icon']} {typ}</span>
      <span style="margin-left:auto;font-weight:700;font-size:12px;color:#1E293B">{cnt}</span>
    </div>"""

# ── FULL HTML ─────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>dSPACE AutomationDesk — Script Report</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'DM Sans', sans-serif;
    background: #F8FAFC;
    color: #1E293B;
    min-height: 100vh;
  }}

  /* ── Hero ── */
  .hero {{
    background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #0F172A 100%);
    padding: 0;
    position: relative;
    overflow: hidden;
  }}
  .hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(14,165,233,.15) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 20%, rgba(139,92,246,.12) 0%, transparent 50%),
      radial-gradient(ellipse at 60% 90%, rgba(16,185,129,.08) 0%, transparent 40%);
  }}
  .hero-grid {{
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
    background-size: 40px 40px;
  }}
  .hero-content {{
    position: relative;
    z-index: 1;
    padding: 48px 56px 40px;
  }}
  .hero-top {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 32px;
    flex-wrap: wrap;
  }}
  .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(14,165,233,.15);
    border: 1px solid rgba(14,165,233,.3);
    color: #7DD3FC;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 20px;
    margin-bottom: 16px;
  }}
  .hero-badge::before {{
    content: '';
    width: 6px; height: 6px;
    background: #38BDF8;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: .5; transform: scale(1.3); }}
  }}
  .hero h1 {{
    font-family: 'Syne', sans-serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.15;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
  }}
  .hero h1 span {{ color: #38BDF8; }}
  .hero-sub {{
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 0;
    font-weight: 300;
  }}
  .hero-meta {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 11px;
    color: #94A3B8;
    white-space: nowrap;
  }}
  .hero-meta strong {{ color: #E2E8F0; font-size: 13px; display: block; margin-bottom: 2px; }}

  /* ── Stat strip ── */
  .stat-strip {{
    position: relative;
    z-index: 1;
    display: flex;
    gap: 1px;
    background: rgba(255,255,255,.06);
    border-top: 1px solid rgba(255,255,255,.08);
    margin-top: 32px;
  }}
  .stat-item {{
    flex: 1;
    padding: 20px 24px;
    text-align: center;
  }}
  .stat-item:hover {{ background: rgba(255,255,255,.04); }}
  .stat-num {{
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
  }}
  .stat-lbl {{
    font-size: 10px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
  }}

  /* ── Main content ── */
  .main {{ padding: 32px 56px 56px; max-width: 1400px; }}

  /* ── Cards row ── */
  .cards-row {{
    display: grid;
    grid-template-columns: 1fr 1fr 340px;
    gap: 20px;
    margin-bottom: 28px;
  }}
  .card {{
    background: white;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .card-title {{
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #94A3B8;
    margin-bottom: 18px;
  }}

  /* ── Filter bar ── */
  .filter-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }}
  .filter-btn {{
    padding: 6px 14px;
    border-radius: 20px;
    border: 1.5px solid #E2E8F0;
    background: white;
    font-size: 11px;
    font-weight: 600;
    color: #64748B;
    cursor: pointer;
    transition: all .18s;
    font-family: 'DM Sans', sans-serif;
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: #0F172A;
    border-color: #0F172A;
    color: white;
  }}
  .search-box {{
    margin-left: auto;
    padding: 7px 14px;
    border-radius: 8px;
    border: 1.5px solid #E2E8F0;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    color: #334155;
    outline: none;
    width: 220px;
    transition: border .2s;
  }}
  .search-box:focus {{ border-color: #0EA5E9; }}

  /* ── Table ── */
  .table-wrap {{
    background: white;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .table-head {{
    padding: 14px 16px;
    background: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .table-head-title {{
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #1E293B;
  }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{
    padding: 10px 16px;
    text-align: left;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94A3B8;
    background: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
  }}
  .script-row {{
    cursor: pointer;
    transition: background .15s;
  }}
  .script-row:hover td {{ background: #F8FAFC !important; }}
  .script-row:hover .expand-btn {{
    border-color: #0EA5E9 !important;
    color: #0EA5E9 !important;
  }}

  /* ── Impl donut ── */
  .impl-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
  }}
  .impl-item {{
    text-align: center;
    padding: 14px 8px;
    border-radius: 10px;
  }}
  .impl-num {{
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
  }}
  .impl-lbl {{
    font-size: 10px;
    color: #94A3B8;
    margin-top: 3px;
    font-weight: 500;
  }}

  /* ── Canvas donut ── */
  #donutCanvas {{ display: block; margin: 0 auto 16px; }}

  /* footer */
  .footer {{
    margin-top: 48px;
    padding-top: 20px;
    border-top: 1px solid #E2E8F0;
    font-size: 11px;
    color: #CBD5E1;
    text-align: center;
  }}

  @media (max-width: 900px) {{
    .hero-content, .main {{ padding: 24px; }}
    .cards-row {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<!-- ══ HERO ═══════════════════════════════════════════════════ -->
<div class="hero">
  <div class="hero-grid"></div>
  <div class="hero-content">
    <div class="hero-top">
      <div>
        <div class="hero-badge">AutomationDesk HIL Framework</div>
        <h1>Script <span>Inventory</span> Report</h1>
        <p class="hero-sub">Generated test scripts — dSPACE AutomationDesk &nbsp;·&nbsp; HIL Environment</p>
      </div>
      <div class="hero-meta">
        <div>
          <strong>{NOW}</strong>
          Report generated
        </div>
      </div>
    </div>

    <div class="stat-strip">
      <div class="stat-item">
        <div class="stat-num" style="color:#38BDF8">{total}</div>
        <div class="stat-lbl">Total Scripts</div>
      </div>
      <div class="stat-item">
        <div class="stat-num" style="color:#10B981">{by_type.get('CAN',0)}</div>
        <div class="stat-lbl">CAN Tests</div>
      </div>
      <div class="stat-item">
        <div class="stat-num" style="color:#8B5CF6">{by_type.get('LIN',0)}</div>
        <div class="stat-lbl">LIN Tests</div>
      </div>
      <div class="stat-item">
        <div class="stat-num" style="color:#34D399">{by_type.get('MODEL VAR',0)}</div>
        <div class="stat-lbl">Model Vars</div>
      </div>
      <div class="stat-item">
        <div class="stat-num" style="color:#FCD34D">{by_type.get('DIAGNOSTICS',0)}</div>
        <div class="stat-lbl">Diagnostics</div>
      </div>
      <div class="stat-item">
        <div class="stat-num" style="color:#F472B6">{total_lines}</div>
        <div class="stat-lbl">Total Lines</div>
      </div>
    </div>
  </div>
</div>

<!-- ══ MAIN ═══════════════════════════════════════════════════ -->
<div class="main">

  <!-- ── Cards row ── -->
  <div class="cards-row">

    <!-- Implementation Status -->
    <div class="card">
      <div class="card-title">API Activation Status</div>
      <div class="impl-grid">
        <div class="impl-item" style="background:#F0FDF4">
          <div class="impl-num" style="color:#166534">{fully_impl}</div>
          <div class="impl-lbl">Full HIL<br>Active</div>
        </div>
        <div class="impl-item" style="background:#FFFBEB">
          <div class="impl-num" style="color:#92400E">{partial}</div>
          <div class="impl-lbl">Partially<br>Active</div>
        </div>
        <div class="impl-item" style="background:#F8FAFC">
          <div class="impl-num" style="color:#475569">{template}</div>
          <div class="impl-lbl">Template<br>Mode</div>
        </div>
      </div>
      <div style="margin-top:16px;padding-top:16px;border-top:1px solid #F1F5F9">
        <div style="font-size:11px;color:#94A3B8;margin-bottom:8px;font-weight:600">HOW TO ACTIVATE</div>
        <div style="font-size:11px;color:#64748B;line-height:1.6">
          In each script, remove <code style="background:#F1F5F9;padding:1px 5px;border-radius:3px;
          color:#0EA5E9;font-family:'JetBrains Mono',monospace">#</code> before
          <code style="background:#F1F5F9;padding:1px 5px;border-radius:3px;
          color:#0EA5E9;font-family:'JetBrains Mono',monospace">MAPort</code> /
          <code style="background:#F1F5F9;padding:1px 5px;border-radius:3px;
          color:#0EA5E9;font-family:'JetBrains Mono',monospace">CANPort</code> calls
          to connect them to your live HIL hardware.
        </div>
      </div>
    </div>

    <!-- Step coverage -->
    <div class="card">
      <div class="card-title">Test Step Coverage</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        {"".join(f'''
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:80px;font-size:11px;font-weight:600;color:#475569">{step}</div>
          <div style="flex:1;height:8px;background:#F1F5F9;border-radius:4px;overflow:hidden">
            <div style="width:{pct}%;height:100%;background:{col};border-radius:4px"></div>
          </div>
          <div style="width:36px;text-align:right;font-size:11px;font-weight:700;color:{col}">{count}</div>
        </div>''' for step, key, col, count, pct in [
          ("SETUP",    "has_setup",    "#0EA5E9", sum(s["has_setup"] for s in scripts),    int(sum(s["has_setup"] for s in scripts)/total*100)),
          ("EXECUTE",  "has_execute",  "#8B5CF6", sum(s["has_execute"] for s in scripts),  int(sum(s["has_execute"] for s in scripts)/total*100)),
          ("VERIFY",   "has_verify",   "#10B981", sum(s["has_verify"] for s in scripts),   int(sum(s["has_verify"] for s in scripts)/total*100)),
          ("TEARDOWN", "has_teardown", "#F59E0B", sum(s["has_teardown"] for s in scripts), int(sum(s["has_teardown"] for s in scripts)/total*100)),
        ])}
      </div>
      <div style="margin-top:20px;padding-top:16px;border-top:1px solid #F1F5F9">
        <div style="font-size:11px;color:#94A3B8;margin-bottom:8px;font-weight:600">ALL SCRIPTS FOLLOW</div>
        <code style="font-size:11px;color:#0EA5E9;font-family:'JetBrains Mono',monospace;
              background:#F0F9FF;padding:4px 10px;border-radius:6px;display:inline-block">
          setup → execute → verify → teardown
        </code>
      </div>
    </div>

    <!-- Donut chart -->
    <div class="card" style="display:flex;flex-direction:column;align-items:center">
      <div class="card-title" style="align-self:flex-start">Distribution by Type</div>
      <canvas id="donutCanvas" width="150" height="150"></canvas>
      <div style="width:100%">{type_legend}</div>
    </div>

  </div>

  <!-- ── Script table ── -->
  <div class="filter-bar">
    <button class="filter-btn active" onclick="filter('ALL',this)">All ({total})</button>
    {"".join(f'<button class="filter-btn" onclick="filter(&quot;{t}&quot;,this)">{TYPE_META.get(t,{}).get("icon","")}&nbsp;{t} ({c})</button>' for t,c in by_type.items())}
    <input class="search-box" type="text" placeholder="🔍  Search test ID or feature…" oninput="search(this.value)">
  </div>

  <div class="table-wrap">
    <div class="table-head">
      <span class="table-head-title">📂 Generated Scripts — Click any row to view source</span>
      <span style="font-size:11px;color:#94A3B8">{total} scripts &nbsp;·&nbsp; {SCRIPTS_DIR}/</span>
    </div>
    <table id="scriptTable">
      <thead>
        <tr>
          <th>Test ID</th>
          <th>Feature Name</th>
          <th style="text-align:center">Type</th>
          <th>Steps</th>
          <th>HIL Activation</th>
          <th style="text-align:center">Lines</th>
          <th style="text-align:center"></th>
        </tr>
      </thead>
      <tbody id="tableBody">
        {all_rows}
      </tbody>
    </table>
  </div>

  <div class="footer">
    dSPACE AutomationDesk HIL Test Framework &nbsp;·&nbsp;
    Script Report &nbsp;·&nbsp; {NOW} &nbsp;·&nbsp;
    {total} scripts &nbsp;·&nbsp; {total_lines} lines of code
  </div>
</div>

<script>
// ── Donut chart ───────────────────────────────────────────────
(function() {{
  const data = {json.dumps([{"label": t, "count": c, "color": type_colors.get(t,"#6B7280")} for t, c in by_type.items()])};
  const canvas = document.getElementById('donutCanvas');
  const ctx = canvas.getContext('2d');
  const total = data.reduce((s,d) => s+d.count, 0);
  const cx = 75, cy = 75, r = 58, inner = 36;
  let start = -Math.PI/2;
  data.forEach(d => {{
    const angle = (d.count/total)*2*Math.PI;
    ctx.beginPath();
    ctx.moveTo(cx,cy);
    ctx.arc(cx,cy,r,start,start+angle);
    ctx.closePath();
    ctx.fillStyle = d.color;
    ctx.fill();
    start += angle;
  }});
  ctx.beginPath();
  ctx.arc(cx,cy,inner,0,2*Math.PI);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.fillStyle = '#1E293B';
  ctx.font = 'bold 20px Syne, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(total, cx, cy-6);
  ctx.fillStyle = '#94A3B8';
  ctx.font = '9px DM Sans, sans-serif';
  ctx.fillText('SCRIPTS', cx, cy+10);
}})();

// ── Expand/collapse code ──────────────────────────────────────
function toggleCode(idx) {{
  const row = document.getElementById('code-'+idx);
  const btn = document.getElementById('btn-'+idx);
  const vis = row.style.display !== 'none' && row.style.display !== '';
  if(vis) {{
    row.style.display='none'; btn.textContent='▾'; btn.style.transform='';
  }} else {{
    row.style.display=''; btn.textContent='▴'; btn.style.transform='rotate(180deg)';
  }}
}}

// ── Filter ────────────────────────────────────────────────────
let activeFilter = 'ALL';
function filter(type, btn) {{
  activeFilter = type;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}}
function search(q) {{
  applyFilters(q);
}}
function applyFilters(q) {{
  q = (q||document.querySelector('.search-box').value||'').toLowerCase();
  document.querySelectorAll('.script-row').forEach(row => {{
    const txt = row.textContent.toLowerCase();
    const typeCell = row.querySelector('span[style*="border-radius:20px"]');
    const rowType  = typeCell ? typeCell.textContent.trim() : '';
    const typeMatch = activeFilter==='ALL' || rowType.includes(activeFilter);
    const textMatch = !q || txt.includes(q);
    const next = row.nextElementSibling;
    row.style.display = (typeMatch && textMatch) ? '' : 'none';
    if(next && next.id && next.id.startsWith('code-'))
      next.style.display = (typeMatch && textMatch) ? 'none' : 'none';
  }});
}}
</script>

</body>
</html>"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✅  Report saved → {OUT_PATH}")
print(f"    Scripts parsed : {total}")
print(f"    Open in browser: file://{os.path.abspath(OUT_PATH)}")
