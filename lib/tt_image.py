#
# IMG{photo/logo.jpg}		left aligned image
# IMGB{photo/logo.jpg}		left aligned image, with border
# IMGC{photo/logo.jpg}		centered image
# IMGCB{photo/logo.jpg}		centered image with border
# Icon{image}				bordered image, in-line, not centered
#
# Creates an HTML image tag
#
#
import taggedtext

def process_img_tag(root, prefix, postfix):
	tag = root.tag()
	nc = root.num_children()
	if nc != 1:
		n = taggedtext.make_error_node(
			root.filename(),
			root.lineno(),
			root.column(),
			"%s{} tag must have one child not %d" % (tag, nc) )

		n.take_children(root)
		root.morph(n)
		return [root]

	c = root.get_child(0)
	if not c.is_word():
		n = taggedtext.make_error_node(
			root.filename(),
			root.lineno(),
			root.column(),
			"%s{} tag argument not a word" % (tag))

		n.take_children(root)
		root.morph(n)
		return  [root]

	image_file = c.word()

	if tag == 'Icon' or tag == 'IMGCB' or tag == 'IMGB':
		border="BORDER=1"
	else:
		border=""

	n = taggedtext.make_translated_node(
			root.filename(),
			root.lineno(),
			root.column(),
			'%s<IMG %s SRC="%s">' % (prefix, border, image_file),
			postfix)
	root.morph(n)

	return [root]

def run(root):

	eval_functions = {
		'IMG':		( lambda root: process_img_tag(root, '', '') ),
		'IMGB':		( lambda root: process_img_tag(root, '', '') ),
		'IMGC':		( lambda root: process_img_tag(root, '<CENTER>', '</CENTER>') ),
		'IMGCB':	( lambda root: process_img_tag(root, '<CENTER>', '</CENTER>') ),
		'Icon':		( lambda root: process_img_tag(root, '', '') ),
	}

	root.eval(eval_functions)

#	if root.is_tag_named("IMG"):
#		process_img_tag(root, "IMG", "", "")
#
#	elif root.is_tag_named("IMGB"):
#		process_img_tag(root, "IMGB", "", "")
#
#	elif root.is_tag_named("IMGC"):
#		process_img_tag(root, "IMGC", "<CENTER>", "</CENTER>")
#
#	elif root.is_tag_named("IMGCB"):
#		process_img_tag(root, "IMGCB", "<CENTER>", "</CENTER>")
#
#	elif root.is_tag_named("Icon"):
#		process_img_tag(root, "Icon", "", "")
#
#	for child in root.children():
#		run(child)
#
