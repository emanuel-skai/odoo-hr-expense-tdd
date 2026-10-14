#!/usr/bin/env bash
# Cobertura de la suite de hr_expense (63 pruebas) con coverage.py dentro del
# contenedor odoo:19. Odoo no corre como root, así que coverage se instala como
# root y la suite se ejecuta como el usuario odoo. Resultado en docs/evidencia/cobertura.txt
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p docs/evidencia
docker compose run --rm --user root --entrypoint bash odoo -c '
  pip install -q --break-system-packages coverage >/dev/null 2>&1
  cd /tmp && chmod 777 /tmp
  su odoo -s /bin/bash -c "cd /tmp && python3 -m coverage run --data-file=/tmp/.coverage \
    --include=\"*/odoo/addons/hr_expense/*\" --omit=\"*/tests/*,*/__manifest__.py\" \
    /usr/bin/odoo --db_host=\${HOST:-db} --db_user=\${USER:-odoo} --db_password=\${PASSWORD:-odoo} \
    -d tdd_hr_expense_cov -i hr_expense --test-tags /hr_expense --stop-after-init \
    --log-level=warn --without-demo=False" > /tmp/odoo_cov.log 2>&1 || true
  grep -E "odoo.tests.result" /tmp/odoo_cov.log || tail -15 /tmp/odoo_cov.log
  echo
  python3 -m coverage report --data-file=/tmp/.coverage -m --skip-empty | sed "s#/usr/lib/python3/dist-packages/odoo/addons/##"
' | tee docs/evidencia/cobertura.txt
