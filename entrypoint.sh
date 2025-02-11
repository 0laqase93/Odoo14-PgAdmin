#!/bin/bash
set -e

echo "-------------------------------------------------"
echo "Iniciando entrypoint personalizado para Odoo..."
echo "-------------------------------------------------"

echo "Esperando a que la base de datos esté disponible..."
# Espera hasta que PostgreSQL esté listo (usando pg_isready)
until pg_isready -h db -p 5432 -U odoo; do
    echo "La base de datos no está disponible, esperando 1 segundo..."
    sleep 1
done
echo "La base de datos está disponible. Continuando..."

echo "Actualizando todos los módulos de Odoo..."
if ! odoo -u all --stop-after-init -c /etc/odoo/odoo.conf; then
    echo "Error durante la actualización de módulos. Se continúa de todas formas..."
fi

echo "Iniciando el servidor Odoo..."
exec odoo -c /etc/odoo/odoo.conf
