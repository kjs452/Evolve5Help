#
# Code<<_EOF_
# 	printf("Hi!");
# _EOF_
#
# CodeSample<<_EOF_
# 	printf("Hi!");
# _EOF_
#
#
# The 'MutCode' is for kforth mutation bolding. Basically
# to show the mutations.
# It looks for '[E]' meta-tag (convert to bold or something):
# The region surrdounded by [E] indicated the "edit" or program that was mutated.
#
# MutCode<<_EOF_
# 	{ 1 2 3 [E]4[E] }
# _EOF_
#
# MutCode<<_EOF_
#	main: { 8 call 9 call 1 call 9 call over }
#	row1: { call /mod 69 LOOK2 79 ENERGY R4 }
#	[E]row2: { -4 -1 OMOVE EAT GROW ?loop and }[E]
#	row3: { 9 call 9 LOOK-SPORE call 8 8 }
#	row4: { EAT <> negate call }
# _EOF_
#
import taggedtext
import html

#
# Process code here documents
#
def run(root):
	def f(heredoc):
		return html.escape(heredoc)

	def f2(heredoc):
		s = html.escape(heredoc)
		s = s.replace("[E]", "<B>", 1)
		s = s.replace("[E]", "</B>", 1)
		return s

	root.translate_heredoc("Code", "\n<pre>\n", "</pre>\n", f)

	root.translate_heredoc("MutCode", "\n<pre>\n", "</pre>\n", f2)

	root.translate_heredoc("CodeSample",
			'\n<CENTER><TABLE BORDER=1 BGCOLOR="#F9FBDE" WIDTH="70%"><TR><TD ALIGN=LEFT><PRE>\n',
			'</PRE></TD></TABLE></CENTER>\n', f )

	root.translate_heredoc("CodeSampleL",
			'\n<TABLE BORDER=1 BGCOLOR="#F9FBDE" WIDTH="70%"><TR><TD ALIGN=LEFT><PRE>\n',
			'</PRE></TD></TABLE>\n', f )
