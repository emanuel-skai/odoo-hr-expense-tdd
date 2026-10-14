"""HU-1: un mismo comprobante no puede reportarse dos veces (hallazgo H1).

Pruebas unitarias puras (sin ORM ni base de datos) sobre la regla
``es_gasto_duplicado`` de ``models/expense_rules.py``. Se ejecutan con
``unittest`` dentro de Odoo o de forma independiente con ``pytest``
(``scripts/run_pure_tests.sh``).
"""
import unittest

try:  # dentro de Odoo
    from odoo.addons.hr_expense.models.expense_rules import es_gasto_duplicado
except ImportError:  # ejecución independiente (sin Odoo instalado)
    from _pure import expense_rules  # noqa: F401  (ver tests/_pure.py)
    from expense_rules import es_gasto_duplicado


class TestGastoDuplicado(unittest.TestCase):
    """HU-1: un mismo comprobante no puede reportarse dos veces."""

    def setUp(self):
        self.existente = {
            "employee_id": 7,
            "reference": "FAC-0001",
            "date": "2026-10-01",
            "amount": 25000.0,
            "state": "submitted",
        }

    def test_mismo_comprobante_es_duplicado(self):
        nuevo = dict(self.existente)
        self.assertTrue(es_gasto_duplicado(nuevo, [self.existente]))

    def test_distinta_referencia_no_es_duplicado(self):
        nuevo = dict(self.existente, reference="FAC-0002")
        self.assertFalse(es_gasto_duplicado(nuevo, [self.existente]))

    def test_distinta_fecha_no_es_duplicado(self):
        nuevo = dict(self.existente, date="2026-10-02")
        self.assertFalse(es_gasto_duplicado(nuevo, [self.existente]))

    def test_distinto_monto_no_es_duplicado(self):
        nuevo = dict(self.existente, amount=25000.01)
        self.assertFalse(es_gasto_duplicado(nuevo, [self.existente]))

    def test_distinto_empleado_no_es_duplicado(self):
        nuevo = dict(self.existente, employee_id=8)
        self.assertFalse(es_gasto_duplicado(nuevo, [self.existente]))

    def test_gasto_rechazado_no_cuenta_como_duplicado(self):
        rechazado = dict(self.existente, state="refused")
        nuevo = dict(self.existente)
        self.assertFalse(es_gasto_duplicado(nuevo, [rechazado]))

    def test_sin_gastos_existentes_no_es_duplicado(self):
        self.assertFalse(es_gasto_duplicado(dict(self.existente), []))

    def test_referencia_se_compara_sin_espacios_ni_mayusculas(self):
        nuevo = dict(self.existente, reference="  fac-0001 ")
        self.assertTrue(es_gasto_duplicado(nuevo, [self.existente]))


if __name__ == "__main__":
    unittest.main()
