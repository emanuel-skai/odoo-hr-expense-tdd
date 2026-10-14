"""Soporte para correr las pruebas puras sin Odoo instalado.

Las reglas de negocio viven en ``models/expense_rules.py`` y no dependen del
ORM. Dentro de Odoo se importan como ``odoo.addons.hr_expense.models.expense_rules``;
fuera de Odoo este módulo deja ``models/`` en ``sys.path`` para importarlas
directamente (``from expense_rules import ...``).
"""
import os
import sys

_MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "models")
if _MODELS not in sys.path:
    sys.path.insert(0, _MODELS)

try:
    import expense_rules  # noqa: F401
except ImportError:  # fase roja: el módulo de producción todavía no existe
    expense_rules = None
