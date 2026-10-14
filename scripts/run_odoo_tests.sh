#!/usr/bin/env bash
# Corre la suite de Odoo del módulo hr_expense (incluye las pruebas TransactionCase
# del incremento) en contenedores y deja el log en docs/evidencia/<nombre>.log
# Uso: scripts/run_odoo_tests.sh [nombre_log]   (por defecto: odoo_tests)
#      TEST_TAGS="/hr_expense:TestAccesoGastosAjenos" scripts/run_odoo_tests.sh hu3_rojo   (solo una clase)
set -euo pipefail
cd "$(dirname "$0")/.."
NAME="${1:-odoo_tests}"
export TEST_TAGS="${TEST_TAGS:-/hr_expense}"
LOG="docs/evidencia/${NAME}.log"
docker compose down -v --remove-orphans >/dev/null 2>&1 || true
docker compose run --rm odoo 2>&1 | tee "$LOG" | grep -E "ERROR|FAIL|Ran [0-9]+ tests|tests? .* (passed|failed)|Modules loaded|hr_expense: [0-9]+ tests" || true
docker compose down -v --remove-orphans >/dev/null 2>&1 || true
echo "---- resumen ($LOG) ----"
grep -E "^.*(odoo\.tests\.result|odoo\.tests\.runner|odoo\.modules\.loading).*(tests|failed|error)" "$LOG" | tail -5
