#
# List tags:
#
# BulletList{
# }
#
# NumberedList{
# }
#
# LetteredList{
# }
#
# RomanNumeralList{
# }
#
#
# Each list tag must be populated with zero or more
# Items using the Item tag:
#
# Item{
#	This is some text, just like would appear in a paragraph.
# }
#
# Item{
#	LH{Heading Crap}
#	This is some text, just like would appear in a paragraph.
#	P{ More stuff to talk about }
#	IMG{ etc crap.jpg }
# }
#
# Item{
#	H{Heading Crap}
#	This is some text, just like would appear in a paragraph.
#	P{ More stuff to talk about }
#	IMG{ etc crap.jpg }
# }
#
#	LH{Heading Crap}		<--- New-line after LH{} tex. No new-line after body.
#
#	H{Heading Crap}			<--- No new-line after H{}. New-line after Body.
#
#	S{Heading Crap}			<--- No new-line after S{}. No new-line after body.
#
#	LL{Heading Crap}		<--- New-line after LL{}. New-line after body.
#
#
import taggedtext

def get_list_heading(n):
	title = None
	new_children = []
	for child in n.children():
		if child.is_tag_named("LH") \
				or child.is_tag_named("H") \
				or child.is_tag_named("S") \
				or child.is_tag_named("LL"):
			if title != None:
				err = taggedtext.make_error_node(
					child.filename(),
					child.lineno(),
					child.column(),
					"Multiple list heading LH{}, H{} tags found inside of Item{} tag, at most one allowed")
				child.morph(err)
				return None
			title = child
		else:
			new_children.append(child)

	if title == None:
		return None
	else:
		n.set_children(new_children)
		return title

def eval_list(root, begin_txt, end_txt):

	error_count = 0
	for child in root.children():
		if child.is_tag_named("Item"):

			title = get_list_heading(child)

			trailerStr1 = "\n</li>\n"
			if title != None:
				if title.is_tag_named("H") or title.is_tag_named("LL"):
					trailerStr1 = "\n</li><br>\n"

			n = taggedtext.make_translated_node(
					child.filename(),
					child.lineno(),
					child.column(),
					"\n<li>\n", trailerStr1)
			n.take_children(child)
			child.morph(n)

			if title != None:
				if title.is_tag_named("LH") or title.is_tag_named("LL"):
					trailerStr2 = "</b><br>"
				else:
					trailerStr2 = "</b>"

				tn = taggedtext.make_translated_node(
					title.filename(),
					title.lineno(),
					title.column(),
					"<b>", trailerStr2)
				tn.take_children(title)
				child.add_child_front(tn)

		else:
			n = taggedtext.make_error_node(
					child.filename(),
					child.lineno(),
					child.column(),
					"A %s{} list tag can only contain Item{} tags" % (root.tag()))
			n.take_children(child)
			child.morph(n)
			error_count += 1

	if error_count > 0:
		return [root]

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
			'BulletList':			(lambda root: eval_list(root, '<ul>', '</ul>')),
			'NumberedList':			(lambda root: eval_list(root, '<ol>', '</ol>')),
			'LetteredList':			(lambda root: eval_list(root, '<ol type="a">', '</ol>')),
			'RomanNumeralList':		(lambda root: eval_list(root, '<ol type="i">', '</ol>')),
	}

	root.eval(eval_functions)
