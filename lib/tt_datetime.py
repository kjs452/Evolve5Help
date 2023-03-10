#
# Macros that expand to the current date/time or the 
# date/time of the last git commit of the document.
#
# NowDT{}	<--- replaced with current date/time as these words:
# 
# Sat Dec 24 08:22:26 EST 2016
#
# GitTimeStamp{}		<--- relpaced with git last modification
#		Mon Jan 16 10:52:10 2017 -0500
#
# GitDate{}
#		December 2nd, 2017
#
# GitDateTime{}
#		2017-02-27_10:53:10
#
# GitYear{}
#			2018
# NowYear{}
#		2018
#
# RootFileName{}
#		foobar.tt		<-- returns BASENAME of the root filename
#
import taggedtext
import datetime
import subprocess
import re
import os

######################################################################
#
#
#
def process_NowDT(node):
	def mk_word(d, fmt, node):
		word = d.strftime(fmt)

		if len(word) == 0:
			# timezone is blank, don't add a blank word, break tt_words
			#print("DEBUG: Timezone is blank, what to do?????")
			word = "EST"

		return taggedtext.make_word_node(
				node.filename(),
				node.lineno(),
				node.column(),
				word )

	nc = node.num_children()
	if nc != 0:
		n = taggedtext.make_error_node(
				node.filename(),
				node.lineno(),
				node.column(),
				"%s{} doesn't take any arguments (found %d)." % (node.tag(), nc) )
		return [n]

	d = datetime.datetime.now()

	if node.tag() == "NowDT":
		#
		# Now format 'd' into several words:
		#	Sat Dec 24 08:22:26 EST 2016
		#
		#	%a			Sat
		#	%b			Dec
		#	%d			24
		#	%H:%M:%S	08:22:26
		#	%Z			EST
		#	%Y			2016
		#
		return [
			mk_word(d, "%a", node),
			mk_word(d, "%b", node),
			mk_word(d, "%d", node),
			mk_word(d, "%H:%M:%S", node),
			mk_word(d, "%Z", node),
			mk_word(d, "%Y", node)
		]

	elif node.tag() == "NowYear":
		return [ mk_word(d, "%Y", node) ]

	else:
		assert True, "unknown tag"

######################################################################
#
# from stack overflow. run a command return list of lines that
# can be iterated over
#
def run_command(command):
	p = subprocess.Popen(command,
			 stdout=subprocess.PIPE,
			 stderr=subprocess.PIPE,
			 shell=True)

	# Read stdout from subprocess until the buffer is empty !
	for line in iter(p.stdout.readline, b''):
		line = line.decode('utf-8')				# KJS ADDED 11/28/2022
		if line: # Don't print blank lines
			yield line

	# This ensures the process has completed, AND sets the 'returncode' attr
	while p.poll() is None:
		sleep(.1) #Don't waste CPU-cycles

	# Empty STDERR buffer
	err = p.stderr.read()
	if p.returncode != 0:
		# The run_command() function is responsible for logging STDERR 
		yield "Error: " + err 

######################################################################
#
#
#
FULL_MONTHS = {
	'Jan': "January",
	'Feb': "February",
	'Mar': "March",
	'Apr': "April",
	'May': "May",
	'Jun': "June",
	'Jul': "July",
	'Aug': "August",
	'Sep': "September",
	'Oct': "October",
	'Nov': "November",
	'Dec': "December",
}

MONTH_NUM = {
	'Jan': "01",
	'Feb': "02",
	'Mar': "03",
	'Apr': "04",
	'May': "05",
	'Jun': "06",
	'Jul': "07",
	'Aug': "08",
	'Sep': "09",
	'Oct': "10",
	'Nov': "11",
	'Dec': "12",
}

DAYS = {
	'1': "1st",
	'2': "2nd",
	'3': "3rd",
	'4': "4th",
	'5': "5th",
	'6': "6th",
	'7': "7th",
	'8': "8th",
	'9': "9th",
	'10': "10th",
	'11': "11th",
	'12': "12th",
	'13': "13th",
	'14': "14th",
	'15': "15th",
	'16': "16th",
	'17': "17th",
	'18': "18th",
	'19': "19th",
	'20': "20th",
	'21': "21th",
	'22': "22nd",
	'23': "23rd",
	'24': "24th",
	'25': "25th",
	'26': "26th",
	'27': "27th",
	'28': "28th",
	'29': "29th",
	'30': "30th",
	'31': "31st",
}

######################################################################
#
# return an array of nodes containing words (or an error node)
#
# 'strs' is an array of string in this format:
#		Mon Jan 16 10:52:10 2017 -0500
#
# 'node' is the tag node
#
def make_date_node_list(node, strs):

	if node.tag() == "GitTimeStamp":
		warr = strs

	elif node.tag() == 'GitDate':
		warr = [ FULL_MONTHS[strs[1]], DAYS[strs[2]] + ",", strs[4] ]

	elif node.tag() == 'GitDateTime':
		warr = [ "%s-%s-%02d_%s" % (
						strs[4],
						MONTH_NUM[strs[1]],
						int(strs[2]),
						strs[3] ) ]

	elif node.tag() == 'GitYear':
		warr = [ strs[4] ]

	else:
		n = taggedtext.make_error_node(
					node.filename(),
					node.lineno(),
					node.column(),
					"%s{} unknown tag name. Expecting GitDate, GitDateTime, GitTimeStamp, GitYear." % (node.tag()))
		return [n]

	result = []
	for w in warr:
		wn = taggedtext.make_word_node(
			node.filename(),
			node.lineno(),
			node.column(),
			w )

		result.append(wn)

	return result

######################################################################
#
# Look at the git log of the current file
#
# Note: Uses the root filename, not the fiename associated with the tag.
#
def process_GitLastModified(node):

	nc = node.num_children()
	if nc != 0:
		n = taggedtext.make_error_node(
				node.filename(),
				node.lineno(),
				node.column(),
				"%s{} doesn't take any arguments (found %d)." % (node.tag(), nc) )
		return [n]

	for line in run_command("git log -1 %s" % (node.get_root().filename())):
		m = re.match(r'^Date:\s*(.*)\s$', line)
		if m != None:
			warr = m.group(1).split()
			return make_date_node_list(node, warr)

	n = taggedtext.make_error_node(
			node.filename(),
			node.lineno(),
			node.column(),
			"%s{} unable to resolve to git change date" % (node.tag()) )
	return [n]

def process_RootFileName(node):
	fn = os.path.basename( node.get_root().filename() )
	n = taggedtext.make_word_node(
			node.filename(),
			node.lineno(),
			node.column(),
			fn )
	return [n]

def run(root):
	eval_functions = {
		'NowDT':			(lambda root: process_NowDT(root)),
		'NowYear':			(lambda root: process_NowDT(root)),
		'GitTimeStamp':		(lambda root: process_GitLastModified(root)),
		'GitDate':			(lambda root: process_GitLastModified(root)),
		'GitDateTime':		(lambda root: process_GitLastModified(root)),
		'GitYear':			(lambda root: process_GitLastModified(root)),
		'RootFileName':		(lambda root: process_RootFileName(root)),
	}

	root.eval(eval_functions)
