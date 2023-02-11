#!/bin/sh
#
# Rebuild unit test file
#
ROOT=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help
LIB=${ROOT}/lib
BIN=${ROOT}/bin
INPUT=${ROOT}/input
OUTPUT=${ROOT}/output
THIRD_PARTY=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help/TURD
DST=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Test/Evolve5Test

export PYTHONPATH=${PYTHONPATH}:${LIB}:${BIN}:${THIRD_PARTY}

#
# Render unit test file(s) files to output
#
cd $INPUT
$BIN/render_code.py $INPUT/unittests.tmpl $OUTPUT UNIT_TESTS.tt

if [ $? = 0 ]; then
	#cat $OUTPUT/UNIT_TESTS.cpp
	echo cp $OUTPUT/UNIT_TESTS.cpp $DST
	cp $OUTPUT/UNIT_TESTS.cpp $DST
else
	echo error will not cat $OUTPUT/UNIT_TESTS.cpp
fi
