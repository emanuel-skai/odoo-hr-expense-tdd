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
    """Dos gastos describen el mismo comprobante si coinciden empleado,
    referencia (sin espacios ni mayúsculas), fecha y monto."""
    return (
        a.get("employee_id") == b.get("employee_id")
        and _normalizar_referencia(a.get("reference")) == _normalizar_referencia(b.get("reference"))
        and str(a.get("date") or "") == str(b.get("date") or "")
        and abs(float(a.get("amount") or 0) - float(b.get("amount") or 0)) < TOLERANCIA_MONTO
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
