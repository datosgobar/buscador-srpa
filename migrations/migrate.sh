#!/bin/bash

this_folder=$(dirname $0)
dump_path="$(dirname $0)/data.sql"
path_to_db="${this_folder}/../app/db.sqlite"

echo "Realizando dump desde ${path_to_db} a ${dump_path}";
${this_folder}/make_dump.sh ${path_to_db} > ${dump_path};

echo "Eliminando db vieja";
rm ${path_to_db};

echo "Creando nueva db";
export SMTP_PASS='';
. "${this_folder}/../venv/bin/activate";
python -W ignore "${this_folder}/../main.py" create_db;

echo "Importando dump";
sqlite3 ${path_to_db} < ${dump_path};
rm data.sql
