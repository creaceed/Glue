# Copyright (c) 2017-2019 Creaceed SPRL and other Glue contributors.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Creaceed SPRL nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL CREACEED SPRL BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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
def cyan(text):
	return tagged(text, Style.CYAN)

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
