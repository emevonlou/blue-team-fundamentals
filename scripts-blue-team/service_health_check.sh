#!/bin/bash

REPORT="../reports/service_health_$(date +%Y-%m-%d).txt"

SERVICES=(
  sshd
  firewalld
  crond
)

# Simulation: set SIMULATE_DOWN="crond" (or any service name) to force NOT RUNNING
SIMULATE_DOWN="${SIMULATE_DOWN:-}"

echo "Service Health Check" > "$REPORT"
echo "--------------------" >> "$REPORT"
echo "Date: $(date)" >> "$REPORT"
echo "" >> "$REPORT"
if [ -n "$SIMULATE_DOWN" ]; then
  echo "Simulation: forcing '$SIMULATE_DOWN' as NOT RUNNING" >> "$REPORT"
  echo "" >> "$REPORT"
fi

for SERVICE in "${SERVICES[@]}"; do
    if [ -n "$SIMULATE_DOWN" ] && [ "$SERVICE" = "$SIMULATE_DOWN" ]; then
        echo "$SERVICE: NOT RUNNING (SIMULATED)" >> "$REPORT"
        continue
    fi

    STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null)

    if [ "$STATUS" = "active" ]; then
        echo "$SERVICE: RUNNING" >> "$REPORT"
    else
        echo "$SERVICE: NOT RUNNING" >> "$REPORT"
    fi
done

echo "" >> "$REPORT"
echo "Health check completed." >> "$REPORT"

echo "Service health report saved to $REPORT"

