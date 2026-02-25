#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import glob
import os
from datetime import datetime
from statistics import mean

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(__file__)
REPORTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "reports"))

PATTERN = os.path.join(REPORTS_DIR, "auth_summary_*.csv")
PNG_OUT = os.path.join(REPORTS_DIR, "auth_failed_attempts_trend.png")
HTML_OUT = os.path.join(REPORTS_DIR, "dashboard_auth.html")

# Severity thresholds (same logic as your risk assessment)
LOW_MAX = 5
MED_MAX = 20


def _safe_int(value: str) -> int:
    """
    Converte strings como "12", "12.0", "  12  " em int.
    Se não der, retorna 0.
    """
    if value is None:
        return 0
    s = str(value).strip()
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def read_rows():
    """
    Lê todos os CSVs auth_summary_*.csv e retorna lista de tuplas: (date_str, failed_attempts_int)
    Espera colunas: date, failed_attempts
    """
    rows = []
    for path in sorted(glob.glob(PATTERN)):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                d = (r.get("date") or "").strip()
                if not d:
                    continue
                a = _safe_int(r.get("failed_attempts"))
                rows.append((d, a))
    return rows


def moving_average(values, window=7):
    """
    Média móvel com o MESMO tamanho de values (começa com janela menor no início),
    igual ao seu script original, só mais seguro.
    """
    if window <= 1:
        return list(values)

    out = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        out.append(mean(values[start : i + 1]))
    return out


def classify(attempts: int) -> str:
    if attempts > MED_MAX:
        return "HIGH"
    if attempts > LOW_MAX:
        return "MEDIUM"
    return "LOW"


def main():
    # garante pasta reports/
    os.makedirs(REPORTS_DIR, exist_ok=True)

    rows = read_rows()
    if not rows:
        print(f"No CSV summaries found at: {PATTERN}")
        return

    # Aggregate by date
    agg = {}
    for d, a in rows:
        # se data não estiver no formato esperado, ignora essa linha (não quebra o script todo)
        try:
            datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            continue
        agg[d] = agg.get(d, 0) + a

    if not agg:
        print("CSV files found, but no valid rows with date format YYYY-MM-DD.")
        return

    dates = sorted(agg.keys())
    x = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    y = [agg[d] for d in dates]
    y_ma7 = moving_average(y, window=7)

    latest_date = dates[-1]
    latest_value = y[-1]
    latest_level = classify(latest_value)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 4.5))

    ax.plot(x, y, marker="o", label="Daily failed attempts")
    ax.plot(x, y_ma7, label="7-day moving average")

    # Severity guide lines
    ax.axhline(LOW_MAX, linestyle="--", linewidth=1.0, label=f"LOW max ({LOW_MAX})")
    ax.axhline(MED_MAX, linestyle="--", linewidth=1.0, label=f"MED max ({MED_MAX})")

    ax.set_title("Failed SSH Login Attempts (Daily)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Failed attempts")

    # ✅ Usa mdates de verdade (isso também remove o warning de “unused import”)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()

    ax.legend()
    fig.tight_layout()
    fig.savefig(PNG_OUT, dpi=150)
    plt.close(fig)

    # Simple HTML report (local)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Auth Dashboard</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, sans-serif; margin: 24px; }}
    code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 6px; }}
    .card {{ border: 1px solid #ddd; border-radius: 12px; padding: 12px; max-width: 860px; }}
    img {{ max-width: 100%; border: 1px solid #eee; border-radius: 12px; padding: 6px; }}
    .muted {{ color: #666; }}
  </style>
</head>
<body>
  <h1>Auth Dashboard</h1>

  <div class="card">
    <p><strong>Latest date:</strong> {latest_date}</p>
    <p><strong>Latest failed attempts:</strong> {latest_value} ({latest_level})</p>
    <p class="muted">
      Thresholds: LOW ≤ {LOW_MAX}, MEDIUM {LOW_MAX+1}–{MED_MAX}, HIGH ≥ {MED_MAX+1}
    </p>
    <h2>Trend</h2>
    <p class="muted">Image saved as <code>{os.path.basename(PNG_OUT)}</code> in <code>reports/</code>.</p>
    <p><img src="{os.path.basename(PNG_OUT)}" alt="Auth trend"></p>

    <h2>Data source</h2>
    <p>Reads <code>reports/auth_summary_*.csv</code>.</p>
  </div>
</body>
</html>
"""

    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard image saved to {PNG_OUT}")
    print(f"Dashboard HTML saved to {HTML_OUT}")


if __name__ == "__main__":
    main()
