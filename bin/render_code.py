#!/usr/bin/python3
#
# render_code.py
# Outputs C code for the instruction_help.cpp and UNIT_TEST.cpp
#
# See usage() for explaination of what this script does.
#
import os
import sys
import re
import jinja2
import taggedtext
import StringIO
import tt_randomtext
import tt_include
import tt_code
import tt_macros
import tt_calculate
import tt_ifthenelse
import tt_unittest
import tt_instruction

RenderCode = False		# this flag is set if the tag RenderCode{} was found

def do_render_code_tag(root, begin_txt, end_txt):
	global RenderCode
	RenderCode = True
	return [ ]

def render_code_run(root):
	eval_functions = {
		'RenderCode':		( lambda root: do_render_code_tag(root, '', '') ),
	}
	root.eval(eval_functions)

def run_codegen_pipeline(root):
	#
	# Early processing:
	# These general things should happen first
	#
	tt_include.run(root, ["."])
	tt_macros.run(root)
	tt_randomtext.run(root)

	#
	# Middle processing
	#
	tt_calculate.run(root)

	render_code_run(root)

	#
	# Late Processing
	#
	tt_ifthenelse.run(root)

	#
	# These filters happen at the end
	#
	tt_instruction.run(root)
	tt_unittest.run(root)

######################################################################
def usage(msg):
	sys.stderr.write("""\
Usage:
   unit_test_generate.py template.tmpl output-dir *.tt

 1st argument must end in .tmpl extension
 2nd argument must be directory
 3rd and subsequent args must end in .tt extension

 This script shall process the .tt files and apply the template
 to them producing a 'outputfile' file.

 Files *.tt must contain "UnitTest{}" tags.

 Example,
	unit_test_generate.pyt unittest.tmpl ../output *.tt

%s
""" % (msg) )

	exit(1)

######################################################################
#
# Return tuple (fhandle, error_string)
# fhandle is None when error happend and error_string is set
#		(None, "error")
#		(filehandle, None)
#
# mode must be "r" or "w"
#
def my_open(filename, mode):
	if mode == 'r':
		if not os.path.exists(filename):
			return (None, "%s: file doesn't exist" % (filename))

		if not os.path.isfile(filename):
			return (None, "%s: is not a file" % (filename))

	try:
		f = open(filename, mode)
		return (f, None)
	except:
		return (None, "%s: exception opening file" % (filename))


######################################################################
def main():
	global RenderCode

	if len(sys.argv) < 4:
		usage("not enough arguments")

	template_file = sys.argv[1]
	output_dir = sys.argv[2]
	files = sys.argv[3:]

	#
	# Check template
	#
	m = re.match(r'^(.*)\.tmpl$', template_file)
	if m == None:
		usage("%s: template file must end with .tmpl extension" % (template_file))

	#
	# Open the HTML jinja2 template file
	#
	ft = my_open(template_file, 'r')
	if ft[0] == None:
		usage(ft[1])

	f = ft[0]

	template_string = f.read()

	f.close()

	if not os.path.isdir(output_dir):
		usage( "%s: not a directory" % (output_dir))

	if len(sys.argv) <= 1:
		sys.stderr.write("No enough arguments\n")
		exit(1)

	#
	# Perform basic sanity check on tagged text input files
	#
	for filename in files:
		m = re.match(r'^(.*)\.tt$', filename)
		if m == None:
			usage("%s: tagged text input file must end with .tt extension" % (filename))

		if not os.path.exists(filename):
			usage("%s: does not exist" % (filename))

		if not os.path.isfile(filename):
			usage("%s: is not a regular file" % (filename))

	#
	# For each tagged text file process it
	# and render it
	#
	for filename in files:
		m = re.match(r'^(.*)\.tt$', filename)
		if m == None:
			usage("%s: Lacks .tt file extension\n" % (filename))

		basename = m.group(1)

		ft = my_open(filename, 'r')
		if ft[0] == None:
			usage(ft[1])

		f = ft[0]
		root = taggedtext.parse(f, filename)
		f.close()

		RenderCode = False

		run_codegen_pipeline(root)

		if not RenderCode:
			continue	# this file did not have the RenderCode{} tag

		error_count = root.report_errors(sys.stderr)
		if error_count > 0:
			exit(1)

		tp = tt_unittest.get_template_parameters()
		if tp == None:
			#
			# error - error message has already printed to stderr
			#
			exit(1)

		tp2 = tt_instruction.get_template_parameters()
		if tp == None:
			#
			# error - error message has already printed to stderr
			#
			exit(1)

		tp['instr'] = tp2

		error_count = root.report_errors(sys.stderr)
		if error_count > 0:
			exit(1)

		if len(tp) == 0:
			sys.stdout.write("Ignoring %s.tt (no MySite. tags found)\n" % (basename))
			continue

		sys.stdout.write("Converting %s.tt -> %s.cpp\n" % (basename, basename))

		tp['basename'] = basename

		output_filename = output_dir + "/" + basename + ".cpp"

		oft = my_open(output_filename, 'w')
		if oft[0] == None:
			sys.stderr.write(oft[1])
			exit(1)

		of = oft[0]

		template = jinja2.Template(template_string)
		rendered_string = template.render(tp)

		of.write(rendered_string)

main()
