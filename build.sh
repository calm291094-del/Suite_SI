#!/usr/bin/env bash
# build.sh - Script de construcción para Render

set -o errexit

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗄️ Ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "📁 Recogiendo archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Build completado!"