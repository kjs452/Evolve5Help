#
# KFORTH Instruction tag
#
# Process a tag like this, and add it to a global database.
# Other tags (mentioned below) will emit various documentation
# and code artifacts from this.
#
# Some fields are options, but most are required.
# Some fields are text only (like name, type, usagee, mode, csymbol)
# Other fields allow full rich tagged text to express the documentation
#		Summary, Inputs, Returns, Description, Energy, Algorithm
#
# Instruction{
#	Name{CMOVE}
#	Type{ CORE | VISION | SMELL | MOVEMENT | EAT | COMMS | QUERY }
#	Usage{	(x y -- rc) }			//{ a usage string }
#	Mode{CMOVE_MODE}
#	CSymbol{Opcode_CMOVE}
#	ReleaseLabel{Boop}				//{ when this instruction was invented } 
#	Min{100}
#	Max{1000}
#
#	Flags{
#		Bit0{0={i cannot eat myself} 1={i can eat myself} }
#		Bit1{0={dsss} 1={sdfddfs} }
#		Bit2{0={i can eat my own strain} 1={i cannot eat my own strain} }
#		Bit15{0={cell to be eaten can be eaten} 1={cell to be eaten, cannot be eaten} }
#	}
#
#	Summary{
#		Increment the Blah Dohicky
#	}
#
#	Inputs{
#		BulletList{
#			Item{}
#			Item{}
#			Item{}
#		}
#	}
#
#	Returns{
#		B{rc} is the numbner of cells Blah'd
#	}
#
#	Description{
#		This should be a complete description of the instruction.
#		Longer than the summary, smaller than Details.
#	}
#
#	Energy{
#		A paragraph or two about how it uses energy.
#		Nothing means nothing.
#	}
#
#	Algorithm{
#		Text describing the algorithm, or a numbered list
#	}
# }
#
# Output Tags:
# These tag produce an HTML output
#
#	InstructionTable{CORE VISION MOVEMENT}
#
#	InstructionDetail{OMOVE}
#	InstructionDetail{swap}
#
#	InstructionDetails{CORE VISION MOVEMENT}
#
#	CCode{}		// KJS TODO	generate static help text structure
#
#
#	InstructionTableOfContents{CORE}		- Table of contents. produce a bulleted list of instructions with links to their 
#
# 	Instruction_Redirect_Pages{}			- expands into Redirect_Make{} tags, one for each instruction.
#
#	InstructionFlags{EAT SEND}			- produce a HTML table documenting the flags
#
#
import taggedtext
import StringIO
import sys
import re

#
# This database is a hash table indexed by the instruction name as a string. "negate2"
#
# Each instruction uses this structure:
#
# Instruction = {
#		'name':				"string",
#		'type':				"string",
#		'usage':			"string",
#		'mode':				"string",
#		'csymbol':			"string",
#		'release_label':	"string",
#		'min':				"string",
#		'max':				"string",
#		'flags':	[
#						[0, 1, node, node]
#						[1, 2, node, node]
#						[2, 4, node, node]
#						[3, 8, node, node]
#						[4, 512, node, node]
#					]
#		}
#
#		'summary':		node,
#		'inputs':		node,
#		'returns':		node,
#		'description':	node,
#		'energy':		node,
#		'algorithm':	node,
#		'help':			[ "ln1", "ln2", "ln3" ]
#		'mask':			"MASK_CORE | MASK_K"
#		'ins':			0,		# computed based on Usage string
#		'outs':			3,		# computed based on Usage string
# }
#
#	InstructionDataBase = {
#		'CMOVE':	InstructionCmove
#		'OMOVE':	InstructionOmove
#		'EAT':		InstructionEat
#	}
#
# Dump table
#
#
InstructionDataBase = {
}

# convert 'n' into an error node, with 'msg'
def make_error(n, msg):
	err = taggedtext.make_error_node(
			n.filename(),
			n.lineno(),
			n.column(),
			msg )
	err.take_children(n)
	n.morph(err)

def read_field(instr, field, n):
	instr[field] = n

def read_words(ss, n):
	for child in n.children():
		if child.is_word():
			ss.write(child.word())
			ss.write(' ')
		else:
			read_words(ss, n)

def read_field_sym(instr, field, n):
	ss = StringIO.StringIO()
	read_words(ss, n)
	instr[field] = ss.getvalue().strip()

def read_sentence(n):
	ss = StringIO.StringIO()
	read_words(ss, n)
	return ss.getvalue().strip()

def make_ccode_mask_string(type):
	result = "MASK_" + type + " | MASK_"
	if type == "CORE":
		result = result + "K"
	elif type == "FIND":
		result = result + "F"
	else:
		result = result + "C"

	return result

USAGE_PAT = re.compile( r'\((.*)--(.*)\)' )

def count_usage(str):
	m = USAGE_PAT.match(str)
	if m != None:
		inputs  = len( m.group(1).strip().split() )
		outputs = len( m.group(2).strip().split() )
		return (inputs, outputs)

	return (0, 0)

#
# 'n' is expected to be something like:
# 'b' is the bit number we are expecting 0..31
# 'bits' is an array to append into on success.
#
# Returns False if an error occured
#
# Bit5{
#	0={...}
#	1={....}
# }
#
#
def read_bit(bits, b, n):
	tag = "Bit" + str(b)

	if not n.is_tag_named(tag):
		make_error(n, "expecting tag named '%s'" % (tag))
		return False

	if n.num_children() != 2:
		make_error(n, "expecting 2 children a 0={} and a 1={}")
		return False

	b0 = n.get_child(0)
	if not b0.is_tag_named("0="):
		make_error(b0, "expecting 0= tag but got this")
		return False

	b1 = n.get_child(1)
	if not b1.is_tag_named("1="):
		make_error(b0, "expecting 1= tag but got this")
		return False

	# str0 = read_sentence(b0)
	# str1 = read_sentence(b1)
	# bits.append( [2**b, str0, str1] )

	bits.append( [b, 2**b, b0, b1] )
	return True

def read_flags(instr, field, n):
	b = 0
	bits = []
	for child in n.children():
		success = read_bit(bits, b, child)
		if not success:
			return False
		b += 1

	instr[field] = bits
	return True

def read_instruction(n, begin_txt, end_txt):
	global InstructionDataBase

	foundField = {
		'Name': False,
		'Type': False,
		'Usage': False,
		'Mode': False,
		'CSymbol': False,
		'ReleaseLabel': False,
		'Min': False,
		'Max': False,
		'Flags': False,
		'Summary': False,
		'Inputs': False,
		'Returns': False,
		'Description': False,
		'Energy': False,
		'Algorithm': False,
		'Help': False,
	}

	instr = { }

	for child in n.children():
		if child.is_tag_named("Key"):
			read_field_sym(instr, 'key', child)
			continue

		if child.tag() not in foundField:
			make_error(child, "Tag %s{} not allowed in Instruction{} tag" % (child.tag()) )
			break

		if child.tag() in foundField:
			found = foundField[child.tag()]
			if found:
				make_error(child, "Duplicate Tag %s{} not allowed in Instruction{} tag" % (child.tag()) )
				break

		foundField[ child.tag() ] = True

		if child.is_tag_named("Name"):
			read_field_sym(instr, 'name', child)
			read_field(instr, 'nameNode', child)

		elif child.is_tag_named("Type"):
			read_field_sym(instr, 'type', child)
			instr['mask'] = make_ccode_mask_string(instr['type'])

		elif child.is_tag_named("Usage"):
			read_field_sym(instr, 'usage', child)
			(ins, outs) = count_usage(instr['usage'])
			instr['ins'] = ins
			instr['outs'] = outs

		elif child.is_tag_named("Mode"):
			read_field(instr, 'mode', child)

		elif child.is_tag_named("CSymbol"):
			read_field_sym(instr, 'csymbol', child)

		elif child.is_tag_named("ReleaseLabel"):
			read_field_sym(instr, 'release_label', child)

		elif child.is_tag_named("Min"):
			read_field_sym(instr, 'min', child)

		elif child.is_tag_named("Max"):
			read_field_sym(instr, 'max', child)

		elif child.is_tag_named("Summary"):
			read_field(instr, 'summary', child)

		elif child.is_tag_named("Inputs"):
			read_field(instr, 'inputs', child)

		elif child.is_tag_named("Returns"):
			read_field(instr, 'returns', child)

		elif child.is_tag_named("Description"):
			read_field(instr, 'description', child)

		elif child.is_tag_named("Energy"):
			read_field(instr, 'energy', child)

		elif child.is_tag_named("Algorithm"):
			read_field(instr, 'algorithm', child)

		elif child.is_heredoc_named("Help"):
			instr['help'] = child.heredoc_content()

		elif child.is_tag_named("Flags"):
			read_flags(instr, 'flags', child)

		if 'key' not in instr:
			instr['key'] = instr['name']

	errors = ""
	for f in foundField:
		if foundField[f] == False:
			errors += ("missing required tag %s inside of Instruction{}\n" % f)

	if errors != "":
		make_error(n, errors)
		return [n]

	name = instr['name']
	key = instr['key']

	if key in InstructionDataBase:
		prev_instr = InstructionDataBase[name]
		locstr = prev_instr['nameNode'].location_string()
		make_error(n, "Instruction duplicated %s (Previous %s)" % (name, locstr))

	#print("KJS DEBUG Instruction ....'%s'" % (instr) )

	InstructionDataBase[key] = instr

	return [n]

def add_child_str(n, str):
	word = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				str,
				'' )
	n.add_child_back(word)

#
# InstructionTable{CORE}
# InstructionTable{CORE VISION HEARING MOVEMENT}
#
def instruction_table(n, begin_txt, end_txt):
	types = [ ]
	for child in n.children():
		if child.is_word():
			types.append(child.word())

	#
	# Table node
	#
	table = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<CENTER><TABLE  BORDER=1 WIDTH="80%">',
				'</TABLE></CENTER>')

	#
	# HEADER ROW
	#
	hdr = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TR BGCOLOR=#10f050>',
				'')
	table.add_child_back(hdr)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT><B>INSTRUCTION</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT><B>USAGE</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT WIDTH="40%"><B>DESCRIPTION</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	#
	# ROWS
	#
	for instr_name in InstructionDataBase:
		instr = InstructionDataBase[instr_name]

		if not instr['type'] in types:
			continue

		row = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TR>',
				'')
		table.add_child_back(row)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT><B>',
				'</B></TD>' )
		add_child_str(col, instr['name'])
		row.add_child_back(col)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT>',
				'</TD>' )
		add_child_str(col, instr['usage'])
		row.add_child_back(col)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT>',
				'<P></TD>' )
		col.add_child_back(instr['description'])
		row.add_child_back(col)

	return [table]

def make_instruction_detail(n, instr):

	root = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<A NAME="ref_%s">' % (instr['name']),
				'<P><HR><P>' )

	title = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<H2>%s</H2>' % (instr['name']),
				'' )
	root.add_child_back(title)

	usage = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<B>Usage:</B> %s<P>' % (instr['usage']),
				'' )
	root.add_child_back(usage)

	summary = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'',
				'<P>' )
	summary.add_child_back( instr['summary'] )
	root.add_child_back(summary)

	description = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'',
				'<P>' )
	description.add_child_back( instr['description'] )
	root.add_child_back(description)

	algo = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'',
				'<P>' )
	algo.add_child_back( instr['algorithm'] )
	root.add_child_back(algo)

	ret = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<B>RETURNS:</B>',
				'<P>' )
	ret.add_child_back( instr['returns'] )
	root.add_child_back(ret)

	energy = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<B>ENERGY:</B>',
				'<P>' )
	energy.add_child_back( instr['energy'] )
	root.add_child_back(energy)

	flags = instr['flags']
	if len(flags) > 0:
		m = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<B>%s MODE BITS:</B>' % (instr['name']),
				'<P>' )
		root.add_child_back(m)

		ft = make_flag_table(n, instr)
		root.add_child_back(ft)

	return root

#
# InstructionDetail{OMOVE}
#
def instruction_detail(n, begin_txt, end_txt):
	if n.num_children() != 1:
		make_error(n, "InstructionDetail{INSTR} wrong number of arguments")
		return [n]

	if not n.get_child(0).is_word():
		make_error(n, "InstructionDetail{INSTR} wrong type for 'INSTR'")
		return [n]

	instr_name = n.get_child(0).word()
	if not instr_name in InstructionDataBase:
		make_error(n, "InstructionDetail{%s} not found" % (instr_name) )
		return [n]

	instr = InstructionDataBase[instr_name]

	root = make_instruction_detail(n, instr)

	return [root]

def make_flag_table(n, instr):
	table = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<CENTER><TABLE  BORDER=1 WIDTH="80%">',
				'</TABLE></CENTER>')

	#
	# HEADER ROW
	#
	hdr = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TR BGCOLOR=#10f050>',
				'')
	table.add_child_back(hdr)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT><B>BIT</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT><B>MASK</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT WIDTH="40%"><B>Meaning when bit is 0</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	hcol = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
			'<TD ALIGN=LEFT WIDTH="40%"><B>Meaning when bit is 1</B>',
			'</TD>' )
	hdr.add_child_back(hcol)

	#
	# ROWS
	#
	flags = instr['flags']
	for flag in flags:
		row = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TR>',
				'')
		table.add_child_back(row)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT><B>',
				'</B></TD>' )
		add_child_str(col, str( flag[0] ))
		row.add_child_back(col)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT>',
				'</TD>' )
		add_child_str(col, str( flag[1] ))
		row.add_child_back(col)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT>',
				'<P></TD>' )
		col.add_child_back(flag[2])
		row.add_child_back(col)

		col = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<TD ALIGN=LEFT>',
				'<P></TD>' )
		col.add_child_back(flag[3])
		row.add_child_back(col)

	return table

#
# InstructionFlags{SEND}
#
def instruction_flags(n, begin_txt, end_txt):
	if n.num_children() != 1:
		make_error(n, "InstructionFlags{INSTR} wrong number of arguments")
		return [n]

	if not n.get_child(0).is_word():
		make_error(n, "InstructionFlags{INSTR} wrong type for 'INSTR'")
		return [n]

	instr_name = n.get_child(0).word()
	if not instr_name in InstructionDataBase:
		make_error(n, "InstructionFlags{%s} not found" % (instr_name) )
		return [n]

	instr = InstructionDataBase[instr_name]

	root = make_flag_table(n, instr)
	return [root]


#
# InstructionDetails{HEARING CORE VISION}
#
def instruction_details(n, begin_txt, end_txt):
	types = [ ]
	for child in n.children():
		if child.is_word():
			types.append(child.word())

	newn = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'',
				'' )

	for instr_name in InstructionDataBase:
		instr = InstructionDataBase[instr_name]
		if not instr['type'] in types:
			continue

		i = make_instruction_detail(n, instr)
		newn.add_child_back(i)

	return [newn]

def make_toc_item(n, instr):

	root = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<LI><A HREF="#ref_%s"><B>%s' % (instr['name'], instr['name']),
				'</B></A></LI>' )

	return root

#
# InstructionTableOfContents{HEARING CORE VISION}
#
def instruction_toc(n, begin_txt, end_txt):
	types = [ ]
	for child in n.children():
		if child.is_word():
			types.append(child.word())

	newn = taggedtext.make_translated_node(n.filename(), n.lineno(), n.column(),
				'<UL>',
				'</UL>' )

	for instr_name in InstructionDataBase:
		instr = InstructionDataBase[instr_name]
		if not instr['type'] in types:
			continue

		i = make_toc_item(n, instr)
		newn.add_child_back(i)

	return [newn]

def instruction_redirect_pages(root):
	for instr_name in InstructionDataBase:
		instr = InstructionDataBase[instr_name]

		rm = taggedtext.make_tag_node(root.filename(), root.lineno(), root.column(), "Redirect_Make")

		filename = "ref_" + instr['csymbol'] + ".html"

		if instr['type'] == 'CORE':
			filename2 = "kforth_reference.html"
		elif instr['type'] == 'FIND':
			filename2 = "find_reference.html"
		else:
			filename2 = "organism_reference.html"

		reference = 'ref_' + instr['name']

		f = taggedtext.make_word_node(root.filename(), root.lineno(), root.column(), filename)
		rm.add_child_back(f)

		f2 = taggedtext.make_word_node(root.filename(), root.lineno(), root.column(), filename2)
		rm.add_child_back(f2)

		r = taggedtext.make_word_node(root.filename(), root.lineno(), root.column(), reference)
		rm.add_child_back(r)

		root.add_child_back(rm)

	return [root]

def run(root):
	eval_functions = {
		'Instruction':					( lambda root: read_instruction(root, '', '') ),
		'InstructionTable':				( lambda root: instruction_table(root, '', '') ),
		'InstructionDetail':			( lambda root: instruction_detail(root, '', '') ),
		'InstructionFlags':				( lambda root: instruction_flags(root, '', '') ),
		'InstructionDetails':			( lambda root: instruction_details(root, '', '') ),
		'InstructionTableOfContents':	( lambda root: instruction_toc(root, '', '') ),
		'Instruction_Redirect_Pages':	instruction_redirect_pages,
	}

	root.eval(eval_functions)

def get_template_parameters():
	return InstructionDataBase
