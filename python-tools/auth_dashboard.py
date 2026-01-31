#!/usr/bin/env python3
import csv
import glob
import os
from datetime import datetime
from statistics import mean

import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(__file__)
REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")
PATTERN = os.path.join(REPORTS_DIR, "auth_summary_*.csv")

PNG_OUT = os.path.join(REPORTS_DIR, "auth_failed_attempts_trend.png")
HTML_OUT = os.path.join(REPORTS_DIR, "dashboard_auth.html")

# Severity thresholds (same logic as your risk assessment)
LOW_MAX = 5
MED_MAX = 20

def read_rows():
    rows = []
    for path in sorted(glob.glob(PATTERN)):
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                d = (r.get("date") or "").strip()
                a = (r.get("failed_attempts") or "").strip()
                if not d:
                    continue
                rows.append((d, int(a) if a.isdigit() else 0))
    return rows

def moving_average(values, window=7):
    out = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        out.append(mean(values[start:i+1]))
    return out

def classify(attempts: int) -> str:
    if attempts > MED_MAX:
        return "HIGH"
    if attempts > LOW_MAX:
        return "MEDIUM"
    return "LOW"

def main():
    rows = read_rows()
    if not rows:
        print(f"No CSV summaries found at: {PATTERN}")
        return

    # Aggregate by date
    agg = {}
    for d, a in rows:
        agg[d] = agg.get(d, 0) + a

    dates = sorted(agg.keys())
    x = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    y = [agg[d] for d in dates]
    y_ma7 = moving_average(y, window=7)

    latest_date = dates[-1]
    latest_value = y[-1]
    latest_level = classify(latest_value)

    # Plot
    plt.figure()
    plt.plot(x, y, marker="o", label="Daily failed attempts")
    plt.plot(x, y_ma7, label="7-day moving average")

    # Severity guide lines
    plt.axhline(LOW_MAX, linestyle="--")
    plt.axhline(MED_MAX, linestyle="--")

    plt.title("Failed SSH Login Attempts (Daily)")
    plt.xlabel("Date")
    plt.ylabel("Failed attempts")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.savefig(PNG_OUT)

    # Simple HTML report (local)
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Auth Dashboard</title>
  <style>
    body {{ font-family: sans-serif; margin: 24px; }}
    code {{ background:#f3f3f3; padding:2px 6px; border-radius:6px; }}
    .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; font-weight:600; }}
    .low {{ background:#e8f5e9; }}
    .med {{ background:#fff8e1; }}
    .high {{ background:#ffebee; }}
  </style>
</head>
<body>
  <h1>Auth Dashboard</h1>
  <p><strong>Latest date:</strong> {latest_date}</p>
  <p><strong>Latest failed attempts:</strong> {latest_value}
     <span class="pill {latest_level.lower()}">{latest_level}</span>
  </p>
  <p><strong>Thresholds:</strong> LOW ≤ {LOW_MAX}, MEDIUM {LOW_MAX+1}–{MED_MAX}, HIGH ≥ {MED_MAX+1}</p>

  <h2>Trend</h2>
  <p>Image saved as <code>{os.path.basename(PNG_OUT)}</code> in <code>reports/</code>.</p>
  <img src="{os.path.basename(PNG_OUT)}" alt="Trend chart" style="max-width:100%; border:1px solid #ddd; border-radius:12px;"/>

  <h2>Data source</h2>
  <p>Reads <code>reports/auth_summary_*.csv</code>.</p>
</body>
</html>
"""
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard image saved to {PNG_OUT}")
    print(f"Dashboard HTML saved to {HTML_OUT}")

if __name__ == "__main__":
    main()

