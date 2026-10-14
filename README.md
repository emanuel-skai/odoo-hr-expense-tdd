# Incremento TDD sobre `hr_expense` (Odoo 19.0) — Grupo 1

**PSWE-06 Calidad y Pruebas de Software · Universidad Cenfotec**
Trabajo de desarrollo ágil de software dirigido por pruebas.
Equipo: David Cárdenas Orozco, Rafael Zuniga Vindas, Juan Ignacio González Cortes, Emanuel Hernández Castillo. Profesor: Luis Felipe Soto Cruz.

## 1. Identificación

| Elemento | Descripción |
|---|---|
| Sistema ya evaluado | Odoo 19.0 Community, módulo `hr_expense` (Gestión de Gastos). |
| Repositorio original | [github.com/odoo/odoo](https://github.com/odoo/odoo), rama 19.0 (LGPL-3.0). |
| Copia de trabajo | Este repositorio: `addons/hr_expense` es el módulo tal como viene en la imagen oficial `odoo:19` (19.0-20260908), más el incremento del equipo. |
| Alcance | Cuatro historias de usuario sobre reglas de negocio y control de acceso, cada una desarrollada con su prueba automatizada primero. El código nuevo se limita a `models/` y `tests/`. |

El repositorio es autocontenido: las pruebas puras corren con Python; la suite de Odoo corre en contenedores (`docker compose`).

## 2. Trazabilidad con el análisis previo

| ID | Hallazgo | Atributo ISO/IEC 25010 | Historia |
|---|---|---|---|
| H1 | Riesgo de contabilizar o pagar dos veces el mismo comprobante | Funcionalidad adecuada; confiabilidad | HU-1 |
| H2 | Aprobar un gasto sin permisos o saltarse la máquina de estados | Funcionalidad adecuada | HU-2 |
| H3 | Un usuario sin privilegios podría leer o modificar gastos ajenos | Seguridad | HU-3 |
| H4 | Uso de `sudo()` que puede omitir verificaciones de acceso | Seguridad | HU-3 |
| H5 | Montos inválidos dejan información inconsistente | Confiabilidad; corrección funcional | HU-4 |

## 3. Historias de usuario y criterios de aceptación

| ID | Historia | Criterio de aceptación | Dónde |
|---|---|---|---|
| HU-1 | Detectar gasto duplicado (mismo empleado, referencia, fecha y monto) | `es_gasto_duplicado` devuelve verdadero cuando coinciden los cuatro campos con un gasto no rechazado y falso si difiere cualquiera; mínimo 5 pruebas, incluido el caso rechazado. | `models/expense_rules.py`, `tests/test_expense_duplicados.py` (9 pruebas) |
| HU-2 | Solo transiciones de estado permitidas | borrador→enviado, enviado→aprobado o rechazado, aprobado→contabilizado, contabilizado→pagado se aceptan; cualquier otro par lanza error. Se prueba el 100 % de los pares (36). | `models/expense_rules.py`, `tests/test_expense_transiciones.py` (5 pruebas, 36 pares) |
| HU-3 | Un empleado sin privilegios no puede ver, modificar ni aprobar gastos ajenos | Tres pruebas con `TransactionCase`: lectura, escritura y aprobación de un gasto ajeno por un usuario sin grupo producen `AccessError`. | `models/hr_expense.py`, `tests/test_expense_acceso.py` (3 pruebas) |
| HU-4 | Rechazar montos no positivos | -0,01 y 0 se rechazan; 0,01 se acepta. | `models/expense_rules.py`, `tests/test_expense_monto.py` (5 pruebas puras) y `tests/test_expense_monto_odoo.py` (2 pruebas de modelo) |

## 4. Proceso

**Ciclo (en este orden, por historia):** (1) escribir la prueba; (2) ejecutarla y constatar que falla (rojo); (3) implementar lo mínimo para que pase (verde); (4) refactorizar; (5) integrar por *pull request*. El historial de commits separa la prueba de la implementación: `test(HU-n): …` precede siempre a `feat(HU-n): …`.

**Herramientas de prueba.** Las reglas sin dependencia de la base de datos (HU-1, HU-2, HU-4) se prueban con `unittest.TestCase` sobre funciones puras en `models/expense_rules.py`. Las que exigen ORM, grupos y reglas de registro (HU-3 y la integración de HU-4) usan `TransactionCase` de `odoo.tests` sobre una base de prueba aislada.

**Análisis estático.** Ruff con la configuración heredada del repositorio de Odoo (`ruff.toml`). Se ejecuta en cada PR (`.github/workflows/ci.yml`) y la evidencia queda en `docs/evidencia/ruff.txt`.

**Integración.** Una rama por historia (`hu-1-…`, `hu-2-…`, `hu-4-…`, `hu-3-…`) integrada a `main` por pull request al cerrar cada ciclo.

## 5. Cómo ejecutar

```bash
# Pruebas puras (HU-1, HU-2, HU-4): solo Python 3.10+ (19 pruebas, < 1 s)
scripts/run_pure_tests.sh

# Análisis estático
ruff check addons/hr_expense/models/expense_rules.py addons/hr_expense/tests/test_expense_*.py

# Suite completa de Odoo (incluye HU-3 y HU-4 de modelo): Docker
scripts/run_odoo_tests.sh                      # toda la suite de hr_expense
scripts/run_coverage.sh                        # la misma suite bajo coverage.py → docs/evidencia/cobertura.txt
TEST_TAGS="/hr_expense:TestAccesoGastosAjenos" scripts/run_odoo_tests.sh hu3   # una clase
```

Dentro de una instalación de Odoo, las mismas pruebas corren con
`python -m unittest odoo.addons.hr_expense.tests.test_expense_duplicados -v`
o `odoo -d <db> -i hr_expense --test-tags /hr_expense --stop-after-init`.

## 6. Evidencia

Los archivos de `docs/evidencia/` registran cada fase:

| Archivo | Qué demuestra |
|---|---|
| `HU-1_rojo.txt`, `HU-2_rojo.txt`, `HU-4_rojo.txt` | La prueba pura falla antes de escribir el código de producción (`ImportError`/`AssertionError`). |
| `HU-1_verde.txt`, `HU-2_verde.txt`, `HU-4_verde.txt` | La misma prueba pasa tras la implementación mínima. |
| `baseline_hr_expense.resumen.log` | Línea base de la suite existente del módulo: 58 pruebas, 0 fallos, 0 errores. |
| `HU-3_HU-4_rojo.resumen.log` | Suite en Docker con las pruebas de modelo nuevas: 2 fallos de 63 (`AccessError not raised`, `UserError not raised`). |
| `HU-3_HU-4_verde.resumen.log` | Suite final con el incremento: 0 fallos, 0 errores de 63 pruebas. |
| `ruff.txt` | Análisis estático sin hallazgos sobre el código nuevo. |
| `cobertura.txt` | Cobertura con coverage.py: 80 % del módulo (1 511 sentencias) con la suite de Odoo y 100 % de `models/expense_rules.py` con las pruebas puras. Se genera con `scripts/run_coverage.sh`. |

**Defectos reales encontrados por las pruebas (fase roja de HU-3 y HU-4).** Las 58 pruebas originales del módulo no cubrían dos comportamientos que el incremento corrige con el mínimo código posible:

1. El usuario designado como *responsable de gastos* de un empleado podía **aprobar** gastos sin pertenecer a ningún grupo de aprobación (`_check_can_approve` solo revisaba el campo calculado `can_approve`). Ahora se levanta `AccessError` si el usuario no tiene `hr_expense.group_hr_expense_team_approver`.
2. `action_submit` aceptaba gastos con **monto negativo** (solo el cero estaba cubierto por la restricción `_check_non_zero`). Ahora un monto negativo levanta `UserError` antes de entrar al flujo de aprobación.

## 7. Historial de integración

| PR | Rama | Historia | Commits |
|---|---|---|---|
| #1 | `hu-1-gastos-duplicados` | HU-1 | `test(HU-1)` → `feat(HU-1)` → `docs` (línea base) |
| #2 | `hu-2-transiciones-estado` | HU-2 | `test(HU-2)` → `feat(HU-2)` |
| #3 | `hu-4-validacion-monto` | HU-4 (reglas puras) | `test(HU-4)` → `feat(HU-4)` |
| #4 | `hu-3-acceso-gastos-ajenos` | HU-3 + HU-4 (modelo) | `chore` (TEST_TAGS) → `test(HU-3, HU-4)` → `chore(docker)` → `feat(HU-3, HU-4)` |

## Licencia

El módulo `hr_expense` es software de Odoo S.A. bajo LGPL-3.0 (ver `LICENSE`). El incremento del Grupo 1 se publica bajo la misma licencia.
