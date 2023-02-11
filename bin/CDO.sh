#!/bin/sh
#
# Rebuild instruction help C code artifacts. copy the files to the Simulator directory
#
ROOT=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help
LIB=${ROOT}/lib
BIN=${ROOT}/bin
INPUT=${ROOT}/input
OUTPUT=${ROOT}/output
THIRD_PARTY=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help/TURD
DST=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5/Simulator

export PYTHONPATH=${PYTHONPATH}:${LIB}:${BIN}:${THIRD_PARTY}

#
# Render unit test file(s) files to output
#
cd $INPUT
$BIN/render_code.py $INPUT/help.tmpl $OUTPUT INSTRUCTIONS/INSTRUCTIONS.tt help.tt

$BIN/render_code.py $INPUT/cell_noops.tmpl $OUTPUT INSTRUCTIONS/INSTRUCTIONS.tt cell_noops.tt

if [ $? = 0 ]; then
	echo cp $OUTPUT/help.cpp $DST
	cp $OUTPUT/help.cpp $DST
	echo cp $OUTPUT/cell_noops.cpp $DST
	cp $OUTPUT/cell_noops.cpp $DST
else
	echo error will not cat $OUTPUT/help.cpp
fi
