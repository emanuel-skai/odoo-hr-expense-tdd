"""HU-4: el sistema rechaza montos no positivos (hallazgo H5).

Pruebas unitarias puras sobre ``monto_valido`` / ``validar_monto`` de
``models/expense_rules.py``, con los valores de borde -0,01, 0 y 0,01.
"""
import unittest

try:  # dentro de Odoo
    from odoo.addons.hr_expense.models.expense_rules import (
        MontoInvalido,
        monto_valido,
        validar_monto,
    )
except ImportError:  # ejecución independiente (sin Odoo instalado)
    from _pure import expense_rules  # noqa: F401
    from expense_rules import MontoInvalido, monto_valido, validar_monto


class TestValidacionMonto(unittest.TestCase):
    """HU-4: un monto de 0 o negativo es rechazado; 0,01 es aceptado."""

    def test_monto_negativo_es_rechazado(self):
        self.assertFalse(monto_valido(-0.01))
        with self.assertRaises(MontoInvalido):
            validar_monto(-0.01)

    def test_monto_cero_es_rechazado(self):
        self.assertFalse(monto_valido(0))
        with self.assertRaises(MontoInvalido):
            validar_monto(0)

    def test_monto_un_centavo_es_aceptado(self):
        self.assertTrue(monto_valido(0.01))
        self.assertEqual(validar_monto(0.01), 0.01)

    def test_monto_vacio_es_rechazado(self):
        self.assertFalse(monto_valido(None))
        with self.assertRaises(MontoInvalido):
            validar_monto(None)

    def test_el_error_informa_el_monto(self):
        with self.assertRaises(MontoInvalido) as ctx:
            validar_monto(-5)
        self.assertIn("-5", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
