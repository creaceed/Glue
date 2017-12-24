
import sys

def raiseError(message):
	exc = Exception()
	exc.message = message
	raise exc
