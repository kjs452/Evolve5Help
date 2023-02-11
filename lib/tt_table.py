#
# Table{
#		TH{Heading0}
#		TH{Heading1}
#		TH{Heading2}
#
#	TD{Row0Col0}
#	TD{Row0Col1}
#	TD{Row0Col2}
#
#	TD{Row1Col0}
#	TD{Row1Col1}
#	TD{Row1Col2}
#
#	TD{Row2Col0}
#	TD{Row2Col1}
#	TD{Row2Col2}
# }
#
# Variants:
#	TD2{}			Table data, highlight the cell.
#
# Produces a html table based on the above pattern.
#
# Variants:
#
# TableL{ }				Don't center, left aligned
# TableLT{ }			Don't center, left aligned, don't highlight header cells, first column is thinner than others
#
# MutationTable{}		Mutation Table format, looks for [E] meta tag for bold
# MergeTable{}			Mutation Table format, looks for [E] meta tag for bold
#
# TableS{}				Slim table, use for simple two column list of numbers
#
#
#
import taggedtext

def make_error(n, errstr):
	err = taggedtext.make_error_node(
		n.filename(),
		n.lineno(),
		n.column(),
		errstr)
	n.morph(err)

def is_header_node(n):
	if not n.is_tag():
		return False
	return n.tag() == "TH"

def is_data_node(n):
	if not n.is_tag():
		return False
	return n.tag() == "TD" \
			or n.tag() == "TD2"

def eval_table(root, begin_txt, end_txt):
	error_count = 0
	column_count = 0
	other_count = 0
	data_count = 0
	for child in root.children():
		if not child.is_tag():
			make_error(root, "Only tags like TH{} TD{} allowed in Table{}")
			return [root]

		if is_header_node(child):
			column_count += 1
		elif is_data_node(child):
			data_count += 1
		else:
			other_count += 1

	if other_count != 0:
		make_error(root, "Only TD{} TD2{} TDC{} and TH{} TH2{} tags allowed in Table{} tag.")
		return [root]

	if column_count == 0:
		make_error(root, "No TH{} tags given, this defines the number of columns.")
		return [root]

	if (data_count % column_count) != 0:
		make_error(root, "Wrong number of TD{} tags (%d) given for the # of columns given (%d)" % (data_count, column_count) )
		return [root]

	if root.is_tag_named("MutationTable"):
		percent_width_first_column = 'WIDTH="%d%%"' % (50)
		bgcolor = ''
		bgcolord = 'BGCOLOR=#F9FBDE'
		width = 'WIDTH="50%"'
		align = 'ALIGN=LEFT'
		border = 'BORDER=1'
		twidth = 'WIDTH="80%"'
	elif root.is_tag_named("TableSlim"):
		percent_width_first_column = 'WIDTH="%d%%"' % (50)
		bgcolor = ''
		bgcolord = ''
		width = ''
		align = 'ALIGN=LEFT'
		border = 'BORDER=1'
		twidth = ''
	else:
		percent_width_first_column = 'WIDTH="%d%%"' % (50)
		bgcolor = 'BGCOLOR=#10f050'
		bgcolord = ''
		width = ''
		align = 'ALIGN=LEFT'
		border = 'BORDER=1'
		twidth = 'WIDTH="80%"'

	if root.is_tag_named("TableLT"):
		percent_width_first_column = 'WIDTH="%d%%"' % (20)

	if root.is_tag_named("MergeTable"):
		percent_width_first_column = 'WIDTH="%d%%"' % (20)
		bgcolor = ''

	first = True
	for child in root.children():
		if child.is_tag_named("TH"):
			if first:
				first = False
				begin_txt	= '<TR %s><TD %s %s>\n' % (bgcolor, align, percent_width_first_column)
				end_txt		= '</TD>\n'
			else:
				begin_txt	= '<TD %s>' % (align)
				end_txt		= '</TD>\n'

			n = taggedtext.make_translated_node(
					child.filename(),
					child.lineno(),
					child.column(),
					begin_txt, end_txt)
			n.take_children(child)
			child.morph(n)

	count = 0
	for child in root.children():
		if child.is_tag_named("TD") or child.is_tag_named("TD2"):
			bb = bgcolord
			if child.is_tag_named("TD2"):
				bb = 'BGCOLOR=#10f050'

			if count % column_count == 0:
				begin_txt	= '<TR>\n<TD ALIGN=LEFT %s %s>\n' % (bb, width)
				end_txt		= '</TD>\n'
			else:
				begin_txt	= '<TD ALIGN=LEFT %s %s>\n' % (bb, width)
				end_txt		= '</TD>\n'

			n = taggedtext.make_translated_node(
					child.filename(),
					child.lineno(),
					child.column(),
					begin_txt, end_txt)
			n.take_children(child)
			child.morph(n)

			count += 1

	if root.is_tag_named("TableL") or root.is_tag_named("TableLT"):
		begin_txt	= '<TABLE %s %s">' % (border, twidth)
		end_txt		= '</TABLE>'
	else:
		begin_txt	= '<CENTER><TABLE %s %s">' % (border, twidth)
		end_txt		= '</TABLE></CENTER>'

	n = taggedtext.make_translated_node(
			root.filename(),
			root.lineno(),
			root.column(),
			begin_txt, end_txt)
	n.take_children(root)
	root.morph(n)
	return [root]

def run(root):
	eval_functions = {
			'Table':			(lambda root: eval_table(root, '', '')),
			'TableL':			(lambda root: eval_table(root, '', '')),
			'TableLT':			(lambda root: eval_table(root, '', '')),
			'MutationTable':	(lambda root: eval_table(root, '', '')),
			'MergeTable':		(lambda root: eval_table(root, '', '')),
			'TableSlim':		(lambda root: eval_table(root, '', '')),
	}

	root.eval(eval_functions)
