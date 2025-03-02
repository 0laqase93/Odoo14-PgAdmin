#!/bin/bash
set -e

echo "-------------------------------------------------"
echo "Iniciando entrypoint personalizado para Odoo..."
echo "-------------------------------------------------"

echo "Esperando a que la base de datos esté disponible..."
export PGPASSWORD=odoo
until pg_isready -h db -p 5432 -U odoo; do
    echo "La base de datos no está disponible, esperando 2 segundos..."
    sleep 2
done
echo "La base de datos está disponible. Continuando..."

echo "Verificando si la base de datos está inicializada..."
# Intenta consultar la tabla; en una base de datos nueva fallará
if ! psql -h db -U odoo -d odoo -c "SELECT 1 FROM ir_module_module LIMIT 1;" &> /dev/null; then
    echo "La base de datos parece vacía o no inicializada. Inicializando Odoo..."
    odoo -d odoo --init=all --stop-after-init -c /etc/odoo/odoo.conf || true
else
    echo "La base de datos ya está inicializada."
fi

echo "Iniciando el servidor Odoo..."
exec odoo -c /etc/odoo/odoo.conf

