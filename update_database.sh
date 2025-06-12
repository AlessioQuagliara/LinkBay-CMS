#!/bin/bash

# 👉 Configura qui i parametri del tuo database
DB_NAME="cms_def"
DB_USER="root"
FLASK_APP="app.py"

echo "💣 Dropping database '$DB_NAME'..."
dropdb $DB_NAME -U $DB_USER

echo "🆕 Creating database '$DB_NAME'..."
createdb $DB_NAME -U $DB_USER

echo "🧹 Rimuovo directory delle migrazioni..."
rm -rf migrations

echo "📦 Re-inizializzo Flask-Migrate..."
export FLASK_APP=$FLASK_APP
flask db init
flask db migrate -m "Reset completo DB"
flask db upgrade

echo "✅ Tutto pronto! Il database '$DB_NAME' è stato ricreato con successo."