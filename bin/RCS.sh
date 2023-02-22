#!/bin/sh
#
# Refresh code samples
#	We copy the code from 'ev5stuff' directory to the 'Evovle5Help/input' directory.
# and expanding tabs.
#
ROOT=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help
LIB=${ROOT}/lib
BIN=${ROOT}/bin
THIRD_PARTY=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help/TURD

SRC=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5/ev5stuff
DST=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help/input

FILES="\
	kforth_bubble.kf		\
	biomorphs.kf			\
	towers_of_hanoi.kf		\
	kforth_bubble.kf		\
	nibbler2.kf				\
	rnd_drawer.kf			\
	shoot3.kf				\
	utank.kf"

for F in $FILES; do



	echo '============================================================================================='
	echo '=====' $F '========================================================================================'
	echo '============================================================================================='

	echo diff $SRC/$F $DST/$F
	diff -w $SRC/$F $DST/$F

	echo '============================================================================================='
	echo '=====' $F '========================================================================================'
	echo '============================================================================================='

done

echo ''
echo ''
echo 'Proceed?  (Press ^C to abort)'

read PROCEED

for F in $FILES; do
	echo expand -t 4 $SRC/$F '>' $DST/$F
	expand -t 4 $SRC/$F > $DST/$F
done
