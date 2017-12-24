
# see https://en.wikipedia.org/wiki/ANSI_escape_code

class Style:
	DARK_RED = '\033[31m'
	DARK_GREEN = '\033[32m'
	RED = '\033[91m'
	GREEN = '\033[92m'
	BLUE = '\033[94m'
	YELLOW = '\033[33m'
	MAGENTA = '\033[35m'
	CYAN = '\033[36m'

	BOLD = '\033[1m'
	ITALIC = '\033[3m'
	UNDERLINE = '\033[4m'

	ENDC = '\033[0m'


def tagged(text, tag):
	return tag + text + Style.ENDC
def tagged2(text, tag, tag2):
	return tag + tag2 + text + Style.ENDC + Style.ENDC

def bold(text):
	return tagged(text, Style.BOLD)

def red(text):
	return tagged(text, Style.RED)

def ok(text):
	return tagged(text, Style.DARK_GREEN)
def error(text):
	return tagged(text, Style.DARK_RED)
def warning(text):
	return tagged(text, Style.YELLOW)

def dependency(text):
	return tagged2(text, Style.BOLD, Style.BLUE)
def revision(text):
	return tagged(text, Style.ITALIC)
def branch(text):
	return tagged(text, Style.BOLD)
