#!/bin/bash
source "$1/../testlib.sh"
set -x

# decide whether a static build was used
IS_STATIC="$(grep STATIC_LINKING:BOOL=ON "${PATH_TO_CSEXEC_LIBS}/../CMakeCache.txt")"

if [[ -z "${IS_STATIC}" ]]; then
    FIND_WHAT="( -name csexec-loader -or -name libcsexec-preload.so )"
fi

while IFS= read -r file; do
    ldd "$file" 2>&1 | grep -E "statically linked|not a dynamic executable" \
        || { ldd "$file"; exit 1; }
done < <(find "${PATH_TO_CSEXEC_LIBS}" -maxdepth 1 -type f -executable ${FIND_WHAT})
