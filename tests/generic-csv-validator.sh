#!/bin/sh

if [ "${PARSER}" = "" ] || \
   [  "${COLUMN_LIST}" = "" ] || \
   [  "${MIN_RECORDS}" = "" ]; then
    echo "$0: Required variables missing." >&2
    exit 1
fi

OUTPUT_FILE=$(mktemp)

cd ..
./polilist --provider=hardcache --include="${PARSER}" --output="${OUTPUT_FILE}" >/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Execution of parser ${PARSER} failed." >&2
    rm ${OUTPUT_FILE}
    exit 1
fi

ERR=0

# Including the header, the total number of lines should be >=MIN_RECORDS+1.
if [ $(wc -l ${OUTPUT_FILE} | cut -d" " -f 1) -le "${MIN_RECORDS}" ]; then
    echo "Parser ${PARSER} returned too few records." >&2
    ERR=1
fi

# Check each expected column exists.
for col in ${COLUMN_LIST}; do
    head -1 ${OUTPUT_FILE} 2>/dev/null | grep ${col} >/dev/null 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Expected column ${col} not produced in output of parser ${PARSER}." >&2
        ERR=1
    fi
done

rm ${OUTPUT_FILE}
exit ${ERR}

