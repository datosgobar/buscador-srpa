#!/bin/sh

SQLITE=sqlite3

if  [ -z "$1" ] ; then
        echo usage: $0  sqlite3.db
        exit
fi

DB="$1"

TABLES=`"$SQLITE" "$DB" .tables`

echo 'BEGIN TRANSACTION;'

for TABLE in $TABLES ; do
        echo 
        echo "-- $TABLE:";
        COLS=`"$SQLITE" "$DB" "pragma table_info($TABLE)" |
        cut -d'|' -f2 `
        COLS_CS=`echo $COLS | sed 's/ /,/g'`
        /bin/echo -e ".mode insert\nselect $COLS_CS from $TABLE;\n" |
        "$SQLITE" "$DB" |
        sed "s/^INSERT INTO table/INSERT INTO $TABLE ($COLS_CS)/" | sed "s/questiontype_id/question_type/"
done
echo 'COMMIT;';
