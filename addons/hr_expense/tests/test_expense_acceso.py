"""HU-3: un empleado sin privilegios no puede ver, modificar ni aprobar gastos
ajenos (hallazgos H3 y H4).

Pruebas con ``TransactionCase`` (vía ``TestExpenseCommon``): usan el ORM, los
grupos y las reglas de registro reales de hr_expense sobre una base de datos
de prueba aislada por transacción. Nunca sobre producción.
"""
from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged
from odoo.tools import mute_logger

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged('-at_install', 'post_install')
class TestAccesoGastosAjenos(TestExpenseCommon):
    """HU-3: lectura, escritura y aprobación de un gasto ajeno por un usuario
    sin grupo de gastos producen AccessError."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Usuario interno SIN ningún grupo de hr_expense (solo base.group_user).
        cls.user_sin_grupo = new_test_user(
            cls.env,
            name='otro_empleado',
            login='otro_empleado',
            email='otro_empleado@example.com',
            groups='base.group_user',
        )
        cls.employee_otro = cls.env['hr.employee'].sudo().create({
            'name': 'otro_empleado',
            'user_id': cls.user_sin_grupo.id,
            'work_contact_id': cls.user_sin_grupo.partner_id.id,
        })
        # Gasto que pertenece a OTRO empleado (expense_employee del fixture).
        cls.gasto_ajeno = cls.create_expenses({'name': 'Gasto ajeno', 'total_amount_currency': 150.0})

    @mute_logger('odoo.addons.base.models.ir_rule')
    def test_lectura_gasto_ajeno_sin_grupo_da_access_error(self):
        with self.assertRaises(AccessError):
            self.gasto_ajeno.with_user(self.user_sin_grupo).read(['name', 'total_amount_currency'])

    @mute_logger('odoo.addons.base.models.ir_rule')
    def test_escritura_gasto_ajeno_sin_grupo_da_access_error(self):
        with self.assertRaises(AccessError):
            self.gasto_ajeno.with_user(self.user_sin_grupo).write({'name': 'modificado por otro'})
        self.assertEqual(self.gasto_ajeno.name, 'Gasto ajeno')

    @mute_logger('odoo.addons.base.models.ir_rule')
    def test_aprobacion_gasto_ajeno_sin_grupo_da_access_error(self):
        """H4: aunque el usuario pueda VER el gasto (es el responsable de gastos
        del empleado), sin el grupo de aprobador no puede aprobarlo: la
        verificación de permisos debe ser de acceso, no una advertencia."""
        self.gasto_ajeno.action_submit()
        self.expense_employee.sudo().expense_manager_id = self.user_sin_grupo
        self.assertEqual(self.gasto_ajeno.state, 'submitted')
        with self.assertRaises(AccessError):
            self.gasto_ajeno.with_user(self.user_sin_grupo).action_approve()
        self.assertEqual(self.gasto_ajeno.state, 'submitted')
