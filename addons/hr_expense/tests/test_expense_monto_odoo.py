"""HU-4 (integración en el modelo): un gasto con monto no positivo no puede
enviarse a aprobación. Complementa las pruebas puras de test_expense_monto.py."""
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged('-at_install', 'post_install')
class TestMontoModelo(TestExpenseCommon):

    def test_enviar_gasto_con_monto_negativo_es_rechazado(self):
        gasto = self.create_expenses({'name': 'Monto negativo', 'total_amount_currency': -0.01})
        with self.assertRaises(UserError):
            gasto.action_submit()
        self.assertEqual(gasto.state, 'draft')

    def test_enviar_gasto_con_un_centavo_es_aceptado(self):
        gasto = self.create_expenses({'name': 'Un centavo', 'total_amount_currency': 0.01})
        gasto.action_submit()
        self.assertIn(gasto.state, ('submitted', 'approved'))
