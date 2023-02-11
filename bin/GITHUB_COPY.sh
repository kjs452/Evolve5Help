#!/bin/sh
#
# Copy the files from the provided manifest file to the destination directory.
#
# Usage: GITHUB_COPY.sh	manifest_file.txt
#
#
SRC=/Users/kjs/DEVELOPMENT/Evolve5
DST=/Volumes/D/GITHUB
ERROR_FILE=/tmp/GHC$$

if [ $# -ne 1 ]; then
	echo Usage: GITHUB_COPY.sh '<manifest-file>'
	exit 1
fi

MANIFEST=$1

if [ ! -f $MANIFEST ]; then
	echo No such file $MANIFEST
	exit 1
fi

#
# PASS 1: Ensure destination directories exists
#
echo Pass 1: check directories exist
ERROR=0
cp /dev/null $ERROR_FILE

for F in `cat $MANIFEST`; do
	REST=`echo $F | sed "s#$SRC/##g"`
	FULL_PATH=$DST/$REST

	DN=`dirname $FULL_PATH`
	if [ ! -d $DN ]; then
		echo $DN >> $ERROR_FILE
		ERROR=1
	fi
done

if [ $ERROR -ne 0 ]; then
	echo These directories do not exist, exiting.
	cat $ERROR_FILE | sort | uniq
	exit 1
fi

echo Pass 2 copy

#
# PASS 2: Copy each file
#
for F in `cat $MANIFEST`; do
	REST=`echo $F | sed "s#$SRC/##g"`
	FULL_PATH=$DST/$REST

	echo cp $F $FULL_PATH
	cp $F $FULL_PATH
done

