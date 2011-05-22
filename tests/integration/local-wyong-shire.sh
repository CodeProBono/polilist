#!/bin/sh

PARSER="local wyong"
COLUMN_LIST="firstname surname email phone level state electorate"
MIN_RECORDS=10

export PARSER COLUMN_LIST MIN_RECORDS

if [ "$(which ./generic-csv-validator.sh 2>/dev/null)" = "" ]; then
    echo "$0: generic-csv-validator.sh not found. Are you running this script from the wrong current directory?" >&2
    exit 1
fi

./generic-csv-validator.sh
exit $?

