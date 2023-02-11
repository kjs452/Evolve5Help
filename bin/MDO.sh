#!/bin/sh
#
# MDO.sh: generate manifest list of files
#
# Usage: MDO.sh <output-filename>
#
# This script writes a list of files that match the rules and directories for
# all the files known to comprise the Evolve5 project.
#

#
# Root directory for where files are located
#
ROOT=/Users/kjs/DEVELOPMENT/Evolve5

TMP_FILE=/tmp/MDO$$.txt

#
# Called with: ProjectDir SubDirs extensions....
#
generate_file_list() {
	DIR1=$1
	DIR2=$2
	shift 2
	for EXT in $*; do
		find $ROOT/$DIR1/$DIR2 -depth 1 | grep "${EXT}$" >> $TMP_FILE
	done
}

#
# Called with: dir file [file ....]
#
generate_files() {
	DIR=$1
	shift 1
	for FILE in $*; do
		find $ROOT/$DIR/$FILE >> $TMP_FILE
	done
}

if [ $# -ne 1 ]; then
	echo Usage: MDO.sh outputfile
	exit 1
fi

OUTPUT_FILE=$1

cp /dev/null $TMP_FILE
if [ $? -ne 0 ]; then
	echo $TMP_FILE not able to create
	exit 1
fi

echo Output file is: $1

generate_file_list		Evolve5Help		bin						.sh	.py
generate_file_list		Evolve5Help		lib						.py
generate_file_list		Evolve5Help		input					.tt .css .tmpl .kf
generate_file_list		Evolve5Help		input/INSTRUCTIONS		.tt
generate_file_list		Evolve5Help		input/blog				.tt
generate_file_list		Evolve5Help		input/IMAGES			.jpg .png .gif
generate_files			Evolve5Help		README.md
generate_files			Evolve5Help		bin/DOIT
generate_files			Evolve5Help		bin/ENV
generate_files			Evolve5Help		bin/blog_maker
generate_files			Evolve5Help		bin/render
generate_files			Evolve5Help		bin/tt
generate_files			Evolve5Help		bin/tt-cmp
generate_files			Evolve5Help		bin/tt-html
generate_files			Evolve5Help		bin/tt-parse
generate_files			Evolve5Help		bin/tt-pretty
generate_files			Evolve5Help		bin/tt-print
generate_file_list		Evolve5Help		TURD					.py
generate_file_list		Evolve5Help		TURD/jinja2				.py
generate_file_list		Evolve5Help		TURD/markupsafe			.py

generate_files			Evolve5			README.md
generate_file_list		Evolve5			Evolve5					.swift .xib
generate_files			Evolve5			Evolve5/Base.lproj
generate_files			Evolve5			Evolve5/Evolve5.entitlements
generate_files			Evolve5			Evolve5/Info.plist
generate_file_list		Evolve5			Simulator				.cpp .h
generate_file_list		Evolve5			bmp						.png .bmp
generate_file_list		Evolve5			help					.html .jpg .gif .css .png
generate_file_list		Evolve5			ev5stuff				.kf .txt

generate_files			Evolve5Batch	README.md
generate_file_list		Evolve5Batch	Evolve5Batch			.cpp .h
generate_file_list		Evolve5Batch	Simulator				.cpp .h
generate_file_list		Evolve5Batch	ev5scripts				.py

#
# Test does not need to be published, it is all derived files
#
#generate_file			Evolve5Test		README.md
#generate_file_list		Evolve5Test		Evolve5Test				.cpp
#generate_file_list		Evolve5Test		Simulator				.cpp .h

sort < $TMP_FILE > $OUTPUT_FILE

/bin/rm -f $TMP_FILE
