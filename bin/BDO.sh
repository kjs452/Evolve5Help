#!/bin/sh
#
# Rebuild BLOG (testing, integrate with DOIT)
#
ROOT=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help
LIB=${ROOT}/lib
BIN=${ROOT}/bin
INPUT=${ROOT}/input
OUTPUT=${ROOT}/output
OUTPUT2=/Volumes/D/www/evolve5/blog
THIRD_PARTY=/Users/kjs/DEVELOPMENT/Evolve5/Evolve5Help/TURD

export PYTHONPATH=${PYTHONPATH}:${LIB}:${BIN}:${THIRD_PARTY}

COPY_TO_MEAT=0

if [ ! -d $OUTPUT ]; then
	echo no such output directory: $OUTPUT
	exit
fi

if [ ! -d $OUTPUT2 ]; then
	echo no such output directory: $OUTPUT2
	exit
fi

if [ $# = 1 ]; then
	if [ $1 = C ]; then
		COPY_TO_MEAT=1
	else
		echo usage: BDO.sh '[C]'
		echo '  C - copy blog files to meat'
		exit
	fi
fi

#
# Render 'tt' files to output
#
cd $INPUT/blog
$BIN/blog_maker $INPUT/blog_index.tmpl $INPUT/blog_each.tmpl $INPUT/common.tt $INPUT/blog/*.tt $OUTPUT/blog

echo cp $INPUT/blog.css $OUTPUT/blog/blog.css
cp $INPUT/blog.css $OUTPUT/blog/blog.css

if [ $COPY_TO_MEAT = 1 ]; then
	echo cp $OUTPUT/blog/* $OUTPUT2
	cp $OUTPUT/blog/* $OUTPUT2
fi
