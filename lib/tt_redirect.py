#
# This filter processes these tagged text tags:
#
# Redirect_Set_Output_Dir{../output}
# Redirect_Make{ref_EXAMPLE.html organism_reference.html ref_CSHIFT}
#
# These tags are removed from the 
#

Dir = "/tmp"

def set_output(root):
	global Dir

	if root.num_children() != 1:
		root.mkerror(root.tag() + "{} requires 1 word as a directory")
		return [root]

	if not root.get_child(0).is_word():
		root.mkerror(root.tag() + "{} argument isn't a word")
		return [root]

	Dir = root.get_child(0).word()

	return []

def redirect_make(root):
	if root.num_children() != 3:
		root.mkerror(root.tag() + "{} requires 3 words as arguments")
		return [root]

	if not root.get_child(0).is_word():
		root.mkerror(root.tag() + "{} 1st argument (filename) isn't a word")
		return [root]

	if not root.get_child(0).is_word():
		root.mkerror(root.tag() + "{} 2nd argument (filename2) isn't a word")
		return [root]

	if not root.get_child(0).is_word():
		root.mkerror(root.tag() + "{} 3rd argument (reference) isn't a word")
		return [root]

	filename = root.get_child(0).word()
	filename2 = root.get_child(1).word()
	reference = root.get_child(2).word()

	str = """
<!DOCTYPE HTML>
<html lang="en-US">
	<head>
		<meta charset="UTF-8">
		<meta http-equiv="refresh" content="0; url={filename2}#{reference}">
		<title>Page Redirection</title>
	</head>
	<body>
		If you are not redirected automatically, follow this <a href='{filename2}#{reference}'>link</a>.
	</body>
</html>
""".format( **{
		'filename2': filename2,
		'reference': reference } )

	# write file
	full_path = Dir + '/' + filename

	f = open(full_path, 'w')
	f.write(str)
	f.close()

	return []

def run(root):
	eval_functions = {
		'Redirect_Set_Output_Dir':	set_output,
		'Redirect_Make':		redirect_make,
	}
	root.eval(eval_functions)
