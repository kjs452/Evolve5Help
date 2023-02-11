#
# Unit test pipeline
#
# We run non-html based processing (like macros, includes, etc...)
#
# Then we run tt_unittest_run() over the document, it doesn't do anything
#
# Then an external caller calls get_template_parameters(root) to
# iterate over the whole document and build up a list of all unit test data.
#
# Process these tags:
#	UnitTest_KFORTH{}
#	UnitTest_CELL{}
#	UnitTest_MUTATION{}
#	UnitTest_MERGE{}
#
# STRUCTURE:
#
#	UnitTest_KFORTH{
#		ProtectedCodeBlocks{4}
#		ProtectedInstructions{dup OMOVE trap9}
#		Code<<_EOF_
#			main: { 2 2 + }
#		_EOF_
#
#		Expected{2}
#		ExpectedError{missing close brace}
#	}
#
#	UnitTest_CELL{
#
#		DeleteInstructions0{OMOVE}				// optional, removes these instrucions from this strains instructions table
#
#		DeleteInstructions1{EXUDE GROW.CB}		// optional
#
#		ProtectedCodeBlocks0{4}					// optional, configure strain 0 protect code blocks and protected instructions
#		ProtectedInstructions0{dup OMOVE trap9}
#
#		ProtectedCodeBlocks1{4}					// optional, configure strain 1 protect code blocks and protected instructions
#		ProtectedInstructions1{dup OMOVE trap9}
#
#		Setup<<_EOF_
#			A[0]->organism->energy = 100;
#			A[0]->energy = 100;
#	
#			B[0]->organism->energy = 200;
#			B[0]->energy = 20;
#		_EOF_
#	
#		Map<<_EOF_
#			#######
#			#..B..#
#			#.c...#
#			#..Ccc#
#			#.....#
#			#....A#
#			#######
#		}
#	
#		AfterMap<<_EOF_
#			#######
#			#..B..#
#			#.c...#
#			#..Ccc#
#			#.....#
#			#....A#
#			#######
#		}
#	
#		Code<<_EOF_
#			main: {
#				255 HOTEST
#				R1! ; y
#				R0! ; x
#				1 R9!
#			}
#		_EOF_
#
#		ACode<<_EOF_         				// optional, program to be loaded into the A strain-0 cell
#			main: { 1 ?loop }
#			other_cells: { 1 ?loop }
#		_EOF_
#
#		Expected{2 2}
#	}
#
#	UnitTest_MUTATION{
#		DeleteInstructions{OMOVE call}
#	
#	    ProtectedCodeBlocks{10} 		//{ can use a symbol name }
#	    Protected_Instructions{OMOVE KFORTH POP FOO BAR}
#	
#	    Probability_Delete{0}
#	    Probability_Duplicate{0}
#	    Probability_Modify{0}
#	    Probability_Insert{100}
#	    Probability_CB{100}
#	    XLEN{100}
#	    MaxApply{1}
#	    Seed{123}
#	    MaxCodeBlocks{100}
#	    Times{1}
#		Seed{123}
#	
#	    Code<<_EOF_
#	    main:
#	    {
#	        1 2 3
#	    }
#	
#	    row1:
#	    {
#	    }
#	    _EOF_
#	
#	    CodeAfter<<_EOF_
#	    main:
#	    {
#	        1 2 3
#	    }
#	
#	    row1:
#	    {
#	    }
#	
#	    row2:
#	    {
#	        -99 494 29
#	    }
#	    _EOF_
# }
#
#	UnitTest_MERGE{
#		Seed{123}
#		MergeMode{0}
#
#	    Code1<<_EOF_
#	    main:
#	    {
#	        1 2 3
#	    }
#	
#	    row1:
#	    {
#	    }
#	    _EOF_
#	
#	    Code2<<_EOF_
#	    main:
#	    {
#	        1 2 3
#	    }
#	
#	    row1:
#	    {
#	    }
#	
#	    row2:
#	    {
#	        -99 494 29
#	    }
#	    _EOF_
#
#	    CodeAfter<<_EOF_
#	    main:
#	    {
#	        1 2 3
#	    }
#	
#	    row1:
#	    {
#	    }
#	
#	    row2:
#	    {
#	        -99 494 29
#	    }
#	    _EOF_
#
#	}
#
# To disable a test, preceed it with a minus,
#
#	-UnitTest_KFORTH{
#	}
#
#	-UnitTest_CELL{
#	}
#
#	-UnitTest_MUTATION{
#	}
#
#	-UnitTest_MERGE{
#	}
# 
#
import taggedtext
import StringIO

# convert 'n' into an error node, with 'msg'
def make_error(n, msg):
	err = taggedtext.make_error_node(
			n.filename(),
			n.lineno(),
			n.column(),
			msg )
	err.take_children(n)
	n.morph(err)

def read_words_helper(ss, n):
	for child in n.children():
		if child.is_word():
			ss.write(child.word())
			ss.write(' ')
		else:
			read_words_helper(ss, n)

def read_words(n):
	ss = StringIO.StringIO()
	read_words_helper(ss, n)
	return ss.getvalue().strip()

def read_words_into_array(n, result):
	for child in n.children():
		if child.is_word():
			result.append(child.word())

def process_kforth(paramdb, id, n):

	# KJS TODO add error checking
	kt = {
		'id': id,
		'file': n.filename(),
		'line': n.lineno() + 1,
	}

	for child in n.children():
		if child.is_tag_named("Expected"):
			if 'expected' in kt:
				child.mkerror("Duplicate Expected{} tag not allowed")

			warr = [ ]
			read_words_into_array(child, warr)
			kt['expected'] = warr

		elif child.is_tag_named("ExpectedError"):
			if 'expected_error' in kt:
				child.mkerror("Duplicate ExpectedError{} tag not allowed")

			kt['expected_error'] = read_words(child)

		elif child.is_heredoc_named("Code"):
			if 'code' in kt:
				child.mkerror("Duplicate Code{} tag not allowed")

			kt['code'] = child.heredoc_content()

		elif child.is_tag_named("ProtectedCodeBlocks"):
			if 'pcb' in kt:
				child.mkerror("Duplicate ProtectedCodeBlocks{} tag not allowed")

			kt['pcb'] = read_words(child)

		elif child.is_tag_named("ProtectedInstructions"):
			if 'pin' in kt:
				child.mkerror("Duplicate ProtectedInstructions{} tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			kt['pin'] = arr

		elif child.is_word():
			n.mkerror("invalid word %s inside of UnitTest_KFORTH{}" % (child.word()));
			return

		else:
			n.mkerror("invalid tag %s{} inside of UnitTest_KFORTH{}" % (child.tag()) )
			return

	paramdb['kforth_tests'].append(kt)

def process_cell(paramdb, id, n):

	ct = {
		'id': id,
		'file': n.filename(),
		'line': n.lineno() + 1,
	}

	for child in n.children():
		if child.is_tag_named("Expected"):
			if 'expected' in ct:
				child.mkerror("Duplicate Expected{} tag not allowed")

			warr = [ ]
			read_words_into_array(child, warr)
			ct['expected'] = warr

		elif child.is_heredoc_named("Code"):
			if 'code' in ct:
				child.mkerror("Duplicate Code{} tag in UnitTest_CELL{}")
				return

			ct['code'] = child.heredoc_content()


		elif child.is_heredoc_named("ACode"):
			if 'acode' in ct:
				child.mkerror("Duplicate ACode{} tag in UnitTest_CELL{}")
				return

			ct['acode'] = child.heredoc_content()

		elif child.is_heredoc_named("Map"):
			if 'map' in ct:
				child.mkerror("Duplicate Map{} tag in UnitTest_CELL{}")
				return

			ct['map'] = child.heredoc_content()

		elif child.is_heredoc_named("AfterMap"):
			if 'aftermap' in ct:
				child.mkerror("Duplicate AfterMap{} tag in UnitTest_CELL{}")
				return

			ct['aftermap'] = child.heredoc_content()

		elif child.is_heredoc_named("Setup"):
			if 'setup' in ct:
				child.mkerror("Duplicate Setup{} tag in UnitTest_CELL{}")
				return

			ct['setup'] = child.heredoc_content()

		elif child.is_tag_named("DeleteInstructions0"):
			if 'del0' in ct:
				child.mkerror("Duplicate DeleteInstuctions0{} tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			ct['del0'] = arr

		elif child.is_tag_named("DeleteInstructions1"):
			if 'del1' in ct:
				child.mkerror("Duplicate DeleteInstructions1{} tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			ct['del1'] = arr

		elif child.is_tag_named("ProtectedInstructions0"):
			if 'pin0' in ct:
				child.mkerror("Duplicate ProtectedInstructions0 tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			ct['pin0'] = arr

		elif child.is_tag_named("ProtectedInstructions1"):
			if 'pin1' in ct:
				child.mkerror("Duplicate ProtectedInstructions1 tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			ct['pin1'] = arr

		elif child.is_tag_named("ProtectedCodeBlocks0"):
			if 'pcb0' in ct:
				child.mkerror("Duplicate ProtectedCodeBlocks0 tag not allowed")

			ct['pcb0'] = read_words(child)

		elif child.is_tag_named("ProtectedCodeBlocks1"):
			if 'pcb1' in ct:
				child.mkerror("Duplicate ProtectedCodeBlocks1 tag not allowed")

			ct['pcb1'] = read_words(child)

		elif child.is_word():
			child.mkerror("invalid word %s inside of UnitTest_CELL{}" % (child.word()) )
			return

		else:
			child.mkerror("invalid tag %s{} inside of UnitTest_CELL{}" % (child.tag()) )
			return

	paramdb['cell_tests'].append(ct)

def process_mutation(paramdb, id, n):

	mt = {
		'id': id,
		'file': n.filename(),
		'line': n.lineno() + 1,
	}

	for child in n.children():
		if child.is_heredoc_named("Code"):
			mt['code'] = child.heredoc_content()

		elif child.is_heredoc_named("CodeAfter"):
			mt['code_after'] = child.heredoc_content()

		elif child.is_tag_named("DeleteInstructions"):
			if 'del' in mt:
				child.mkerror("Duplicate DeleteInstuctions{} tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			mt['del'] = arr

		elif child.is_tag_named("ProtectedInstructions"):
			if 'pin' in mt:
				child.mkerror("Duplicate ProtectedInstructions tag not allowed")

			arr = []
			read_words_into_array(child, arr)
			mt['pin'] = arr

		elif child.is_tag_named("ProtectedCodeBlocks"):
			if 'pcb' in mt:
				child.mkerror("Duplicate ProtectedCodeBlocks tag not allowed")

			mt['pcb'] = read_words(child)

		elif child.is_tag_named("Probability_Delete"):
			if 'pdel' in mt:
				child.mkerror("Duplicate Probability_Delete tag not allowed")

			mt['pdel'] = read_words(child)

		elif child.is_tag_named("Probability_Duplicate"):
			if 'pdup' in mt:
				child.mkerror("Duplicate Probability_Duplicate tag not allowed")

			mt['pdup'] = read_words(child)

		elif child.is_tag_named("Probability_Transpose"):
			if 'ptsp' in mt:
				child.mkerror("Duplicate Probability_Transpose tag not allowed")

			mt['ptsp'] = read_words(child)

		elif child.is_tag_named("Probability_Modify"):
			if 'pmod' in mt:
				child.mkerror("Duplicate Probability_Modify tag not allowed")

			mt['pmod'] = read_words(child)

		elif child.is_tag_named("Probability_Insert"):
			if 'pins' in mt:
				child.mkerror("Duplicate Probability_Insert tag not allowed")

			mt['pins'] = read_words(child)

		elif child.is_tag_named("Probability_CB"):
			if 'prob_cb' in mt:
				child.mkerror("Duplicate Probability_CB tag not allowed")

			mt['prob_cb'] = read_words(child)

		elif child.is_tag_named("XLEN"):
			if 'xlen' in mt:
				child.mkerror("Duplicate XLEN tag not allowed")

			mt['xlen'] = read_words(child)

		elif child.is_tag_named("MaxApply"):
			if 'max_apply' in mt:
				child.mkerror("Duplicate MaxApply tag not allowed")

			mt['max_apply'] = read_words(child)

		elif child.is_tag_named("Seed"):
			if 'seed' in mt:
				child.mkerror("Duplicate Seed tag not allowed")

			mt['seed'] = read_words(child)

		elif child.is_tag_named("MaxCodeBlocks"):
			if 'max_cbs' in mt:
				child.mkerror("Duplicate MaxCodeBlocks tag not allowed")

			mt['max_cbs'] = read_words(child)

		elif child.is_tag_named("Times"):
			if 'times' in mt:
				child.mkerror("Duplicate Times tag not allowed")

			mt['times'] = read_words(child)

		elif child.is_word():
			child.mkerror("invalid word %s inside of UnitTest_MUTATION{}" % (child.word()) )
			return

		else:
			child.mkerror("invalid tag %s{} inside of UnitTest_MUTATION{}" % (child.tag()) )
			return

	paramdb['mutation_tests'].append(mt)

def process_merge(paramdb, id, n):

	mt = {
		'id': id,
		'file': n.filename(),
		'line': n.lineno() + 1,
	}

	for child in n.children():
		if child.is_heredoc_named("Code1"):
			mt['code1'] = child.heredoc_content()

		elif child.is_heredoc_named("Code2"):
			mt['code2'] = child.heredoc_content()

		elif child.is_heredoc_named("CodeAfter"):
			mt['code_after'] = child.heredoc_content()

		elif child.is_tag_named("Seed"):
			if 'seed' in mt:
				child.mkerror("Duplicate Seed tag not allowed")

			mt['seed'] = read_words(child)

		elif child.is_tag_named("MergeMode"):
			if 'merge' in mt:
				child.mkerror("Duplicate MergeMode tag not allowed")

			mt['merge'] = read_words(child)

		elif child.is_word():
			child.mkerror("invalid word %s inside of UnitTest_MERGE{}" % (child.word()) )
			return

		else:
			child.mkerror("invalid tag %s{} inside of UnitTest_MERGE{}" % (child.tag()) )
			return

	paramdb['merge_tests'].append(mt)

#
#
# Iterate over all the unit test tags.
# Construct 
#
# Return a database of keys which are the template
# parameters available in the Jinja2 template.
#
# paramdb = {
#		'kforth_tests':			[ ... { KT } ... ],
#		'cell_tests':			[ ... { CT } ... ],
#		'mutation_tests':		[ ... { MT } ... ],
#		'merge_tests':			[ ... { MERGET } ... ],
# }
#
# KT = {
#	'id': 1000,
#	'file': 'filename.tt'
#	'line': 12		// 1 based
#	'code': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'expected': ['34', ...]
#	'expected_error': 'this is a sentence',
#	'pcb':	9			// protected code blocks
#	'pin':	["OMOVE", "dup", "?loop" ]	// protected instructions
# }
#
# CT = {
#	'id': 2000,
#	'file': 'filename.tt'
#	'line': 12		// 1 based
#	'code': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'acode': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'expected': ['34', ...]
#	'expected_error': 'this is a sentence',
#	'map': [ "", "", "", ""]
#	'aftermap': [ "", "", "", ""]
#	'setup': [ "", "", "", ""]
#	'del0': [ "", "", "", ""]
#	'del1': [ "", "", "", ""]
#	'pin0': [ "", "", "", ""]
#	'pin1': [ "", "", "", ""]
#	'pcb0': "start",
#	'pcb1': 0,
# }
#
# MT = {
#	'id': 3000,
#	'file': 'filename.tt'
#	'line': 12		// 1 based
#	'code': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'code_after': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'del': ["", ""]
#	'pin': ["", ""]
#	'pcb': "start"    or  "12"
#	'pdel': "3.0",
#	'pdup': "3.0",
#	'pmod': "3.0",
#	'ptsp': "2.0",
#	'prob_cb': "25.0"
#	'pins': "3.0",
#	'xlen': "10",
#	'max_apply': "1",
#	'seed': "123",
#	'max_cbs': "100",
#	'times': "1000",
# }
#
# MERGET = {
#	'id': 3000,
#	'file': 'filename.tt'
#	'line': 12		// 1 based
#	'code1': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'code1': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'code_after': ["Kforth Code As a multi-line string", "l2", "line3", ...],
#	'seed': "123",
#	'merge': "0",
# }
#
paramdb = {
		'kforth_tests':		[ ],
		'cell_tests':		[ ],
		'mutation_tests':	[ ],
		'merge_tests':		[ ],
	}

def read_kforth(root, begin_txt, end_txt):
	id = root.lineno()+1
	process_kforth(paramdb, id, root)
	return [root]

def read_cell(root, begin_txt, end_txt):
	id = root.lineno()+1
	process_cell(paramdb, id, root)
	return [root]

def read_mutation(root, begin_txt, end_txt):
	id = root.lineno()+1
	process_mutation(paramdb, id, root)
	return [root]

def read_merge(root, begin_txt, end_txt):
	id = root.lineno()+1
	process_merge(paramdb, id, root)
	return [root]

def run(root):
	eval_functions = {
		'UnitTest_KFORTH':		( lambda root: read_kforth(root, '', '') ),
		'UnitTest_CELL':		( lambda root: read_cell(root, '', '') ),
		'UnitTest_MUTATION':	( lambda root: read_mutation(root, '', '') ),
		'UnitTest_MERGE':		( lambda root: read_merge(root, '', '') ),
	}

	root.eval(eval_functions)

def get_template_parameters():
	return paramdb
