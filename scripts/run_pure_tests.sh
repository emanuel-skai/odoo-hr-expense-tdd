#!/usr/bin/env bash
# Pruebas puras del incremento (HU-1, HU-2, HU-4): unittest, sin Odoo ni base de datos.
# Se corren desde tests/ para cargar cada archivo como módulo de primer nivel
# (tests/__init__.py requiere Odoo). Dentro de Odoo el equivalente es:
#   python -m unittest odoo.addons.hr_expense.tests.test_expense_duplicados -v
set -uo pipefail
cd "$(dirname "$0")/../addons/hr_expense/tests"
MODS="${*:-test_expense_duplicados test_expense_transiciones test_expense_monto}"
python3 -m unittest $MODS -v
