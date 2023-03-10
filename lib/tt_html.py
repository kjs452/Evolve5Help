#!/usr/bin/python
#
# A collection of basic HTML tags
# and other processing for my website
#
import taggedtext
import tt_randomtext
import tt_include
import tt_code
import tt_hdbar
import tt_macros
import tt_words
import tt_datetime
import tt_simple_tags
import tt_links
import tt_taggedtext_logo
import tt_image
import tt_calculate
import tt_lists
import tt_ifthenelse
import tt_table
import tt_instruction
import tt_redirect

def run(root):
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
	tt_datetime.run(root)
	tt_calculate.run(root)

	#
	# Late Processing
	#
	tt_ifthenelse.run(root)

	#
	# These filters happen at the end
	#
	tt_hdbar.run(root)
	tt_simple_tags.run(root)
	tt_code.run(root)
	tt_links.run(root)
	tt_taggedtext_logo.run(root)
	tt_image.run(root)
	tt_lists.run(root)
	tt_table.run(root)

	#
	# Instruction must come before Redirect., and both should come at very end
	#
	tt_instruction.run(root)
	tt_redirect.run(root)

	#
	# word processing should probably happen at the end
	#
	tt_words.run(root)

######################################################################
#
# conditional main() - if called as a command, then run main()
#
def main():
	taggedtext.command(run)

if __name__ == "__main__":
	main()
