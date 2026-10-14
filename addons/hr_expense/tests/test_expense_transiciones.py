"""HU-2: solo existen transiciones de estado permitidas (hallazgo H2).

Pruebas unitarias puras sobre ``transicion_valida`` / ``validar_transicion``
de ``models/expense_rules.py``. Se prueba el 100 % de los pares
(estado origen, estado destino).
"""
import itertools
import unittest

try:  # dentro de Odoo
    from odoo.addons.hr_expense.models.expense_rules import (
        ESTADOS,
        TRANSICIONES_VALIDAS,
        TransicionInvalida,
        transicion_valida,
        validar_transicion,
    )
except ImportError:  # ejecución independiente (sin Odoo instalado)
    from _pure import expense_rules  # noqa: F401
    from expense_rules import (
        ESTADOS,
        TRANSICIONES_VALIDAS,
        TransicionInvalida,
        transicion_valida,
        validar_transicion,
    )

#: Flujo de un gasto según la historia: borrador → enviado → aprobado | rechazado,
#: aprobado → contabilizado, contabilizado → pagado.
PERMITIDAS = {
    ("borrador", "enviado"),
    ("enviado", "aprobado"),
    ("enviado", "rechazado"),
    ("aprobado", "contabilizado"),
    ("contabilizado", "pagado"),
}


class TestTransicionesEstado(unittest.TestCase):
    """HU-2: un gasto no se aprueba ni se paga sin seguir el flujo."""

    def test_los_estados_del_flujo_existen(self):
        self.assertEqual(
            set(ESTADOS),
            {"borrador", "enviado", "aprobado", "rechazado", "contabilizado", "pagado"},
        )

    def test_el_conjunto_de_transiciones_validas_es_exactamente_el_del_flujo(self):
        self.assertEqual(set(TRANSICIONES_VALIDAS), PERMITIDAS)

    def test_todos_los_pares_origen_destino(self):
        """Cubre el 100 % de los pares: 6 estados x 6 estados = 36 combinaciones."""
        pares = list(itertools.product(ESTADOS, ESTADOS))
        self.assertEqual(len(pares), 36)
        for origen, destino in pares:
            with self.subTest(origen=origen, destino=destino):
                esperado = (origen, destino) in PERMITIDAS
                self.assertEqual(transicion_valida(origen, destino), esperado)
                if esperado:
                    validar_transicion(origen, destino)  # no lanza
                else:
                    with self.assertRaises(TransicionInvalida):
                        validar_transicion(origen, destino)

    def test_estado_desconocido_lanza_error(self):
        with self.assertRaises(TransicionInvalida):
            validar_transicion("borrador", "inventado")
        with self.assertRaises(TransicionInvalida):
            validar_transicion("inventado", "enviado")

    def test_el_error_describe_la_transicion(self):
        with self.assertRaises(TransicionInvalida) as ctx:
            validar_transicion("borrador", "pagado")
        self.assertIn("borrador", str(ctx.exception))
        self.assertIn("pagado", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
