# Part of the Grupo 1 TDD increment (PSWE-06). See README.md.
"""Reglas de negocio puras del módulo hr_expense (sin ORM ni base de datos).

Se mantienen fuera de ``hr_expense.py`` a propósito: el análisis previo
encontró la complejidad concentrada en ese archivo, así que el código nuevo
vive en un módulo pequeño, puro y rápido de probar con ``unittest``.

HU-1 (hallazgo H1): detección de gastos duplicados.
"""

#: Estado en el que un gasto deja de contar para la detección de duplicados.
ESTADO_RECHAZADO = "refused"
#: Tolerancia para comparar montos (centavos).
TOLERANCIA_MONTO = 0.005


def _normalizar_referencia(referencia):
    return (referencia or "").strip().upper()


def _mismo_comprobante(a, b):
    """Compara comprobantes solo cuando ambos tienen referencia."""
    if (
        not _normalizar_referencia(a.get("reference"))
        or not _normalizar_referencia(b.get("reference"))
    ):
        return False

    return (
        a.get("employee_id") == b.get("employee_id")
        and _normalizar_referencia(a.get("reference"))
        == _normalizar_referencia(b.get("reference"))
        and str(a.get("date") or "") == str(b.get("date") or "")
        and abs(
            float(a.get("amount") or 0)
            - float(b.get("amount") or 0)
        ) < TOLERANCIA_MONTO
    )


def es_gasto_duplicado(nuevo, existentes):
    """HU-1: ``True`` si ``nuevo`` repite un gasto NO rechazado de ``existentes``.

    :param nuevo: dict con ``employee_id``, ``reference``, ``date`` y ``amount``.
    :param existentes: iterable de dicts con las mismas claves y, opcionalmente,
        ``state`` (los rechazados no cuentan) e ``id`` (se ignora el propio registro).
    """
    for existente in existentes:
        if existente.get("state") == ESTADO_RECHAZADO:
            continue
        if nuevo.get("id") and nuevo.get("id") == existente.get("id"):
            continue
        if _mismo_comprobante(nuevo, existente):
            return True
    return False


# ---------------------------------------------------------------------------
# HU-2 (hallazgo H2): máquina de estados del gasto
# ---------------------------------------------------------------------------

#: Estados del flujo de gastos tal como los describe la historia de usuario.
ESTADOS = ("borrador", "enviado", "aprobado", "rechazado", "contabilizado", "pagado")

#: Equivalencia con los estados del modelo ``hr.expense`` de Odoo 19.
ESTADO_ODOO = {
    "borrador": "draft",
    "enviado": "submitted",
    "aprobado": "approved",
    "rechazado": "refused",
    "contabilizado": "posted",
    "pagado": "paid",
}

#: Únicas transiciones permitidas: cualquier otro par es un error.
TRANSICIONES_VALIDAS = frozenset({
    ("borrador", "enviado"),
    ("enviado", "aprobado"),
    ("enviado", "rechazado"),
    ("aprobado", "contabilizado"),
    ("contabilizado", "pagado"),
})


class TransicionInvalida(ValueError):
    """La transición de estado solicitada no está permitida por el flujo."""


def transicion_valida(origen, destino):
    """HU-2: ``True`` solo si (origen, destino) es una transición del flujo."""
    return (origen, destino) in TRANSICIONES_VALIDAS


def validar_transicion(origen, destino):
    """HU-2: lanza ``TransicionInvalida`` si la transición no está permitida."""
    if not transicion_valida(origen, destino):
        msg = f"Transición no permitida: {origen} → {destino}"
        raise TransicionInvalida(msg)


# ---------------------------------------------------------------------------
# HU-4 (hallazgo H5): validación de monto
# ---------------------------------------------------------------------------

class MontoInvalido(ValueError):
    """El monto del gasto no es un número estrictamente positivo."""


def monto_valido(monto):
    """HU-4: ``True`` solo si ``monto`` es un número mayor que cero."""
    try:
        return float(monto) > 0
    except (TypeError, ValueError):
        return False


def validar_monto(monto):
    """HU-4: devuelve ``monto`` si es válido; si no, lanza ``MontoInvalido``."""
    if not monto_valido(monto):
        msg = f"Monto inválido: {monto!r}. Debe ser mayor que cero."
        raise MontoInvalido(msg)
    return monto
