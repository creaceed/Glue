#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import argparse

from common import *
from dependency import *
from project import *
import style

COMMAND_HELP = "help"
COMMAND_LIST = "list"
COMMAND_STATUS = "status"
COMMAND_RECORD = "record"
COMMAND_ADVANCE = "advance"
COMMAND_UPDATE = "update"
COMMAND_CHECK = "check" # check committed status, fails otherwise
COMMAND_BUILDVERSION = "buildversion" # returns a build version from workspace repository

def prepareLogger(level=logging.DEBUG):
	logging.basicConfig(stream=sys.stderr, level=level, format="%(levelname)s: %(message)s")
	#	logging.debug('A debug message!')
	#	logging.info('We processed records')
def main(argv):
	prepareLogger(logging.DEBUG)
	logging.debug("args = %s", ", ".join(argv))

	# parser = argparse.ArgumentParser(description='Glue: Automating dependent repositories operations.')
	# group = parser.add_mutually_exclusive_group(required=True)
	# group.add_argument('-l', '--list', dest='list', action='store_true', help='Lists all project dependencies, as declared in the %s file.' % (GLUEDEPS_FILENAME))
	# group.add_argument('-s', '--status', dest='status', action='store_true', help='Print status for each dependency.')
	# group.add_argument('-a', '--advance', dest='advance', metavar='dependency', nargs='*', help='Advances passed dependencies to their current branch head. Switching branches must be done manually through versioning scheme.')
	# group.add_argument('-r', '--record', dest='record', action='store_true', help='Record project dependencies and generate new %s file.' % (GLUESTATES_FILENAME))
	# group.add_argument('-u', '--update', dest='update', action='store_true', help='Update project dependencies to given (or current) recorded states.')

	parser = argparse.ArgumentParser(description='Glue: Automating dependent repositories operations.')
	subparsers = parser.add_subparsers(help='sub-command help', dest='command')

	raw_option_help = 'Raw result only, skips descriptive text and formating'

	# List
	help = 'Lists all project dependencies, as declared in the %s file.' % (GLUEDEPS_FILENAME)
	subparser = subparsers.add_parser(COMMAND_LIST, help=help)
	subparser.add_argument('-p', '--print', dest='print', action='store_true', help='Print or not?')

	# Status
	help = 'Print status for each dependency.'
	subparser = subparsers.add_parser(COMMAND_STATUS, help=help)
	subparser.add_argument('-r', '--remote', dest='remote', action='store_true', help='Provides remote status, ie, number of incoming & outgoing changes.')

	# Advance
	help = 'Advances passed dependencies to their current branch head. Switching branches must be done manually through versioning scheme.'
	subparser = subparsers.add_parser(COMMAND_ADVANCE, help=help)
	subparser.add_argument('deps', nargs='*', help='The list of dependencies to advance.')
	subparser.add_argument('-a', '--all', dest='all', action='store_true', help='Advances all dependencies.')

	# Record
	help = 'Record project dependencies and generate new %s file.' % (GLUESTATES_FILENAME)
	subparser = subparsers.add_parser(COMMAND_RECORD, help=help)

	# Update
	help = 'Update project dependencies to given (or current) recorded states.'
	subparser = subparsers.add_parser(COMMAND_UPDATE, help=help)
	subparser.add_argument('-c', '--clean', dest='clean', action='store_true', help='Removes all uncommitted files')

	# Check
	help = 'Check if dependencies are committed, returns error otherwise with list of uncommitted dependencies.'
	subparser = subparsers.add_parser(COMMAND_CHECK, help=help)
	subparser.add_argument('-0', '--raw', dest='raw', action='store_true', help=raw_option_help)

	# Build Version
	help = 'Return the computed build version. The default scheme for the build version is a 2 part string: <A>.<B>, where A is the number of commits leading to the current one, and <B> is decimal value computed from the commit hash. The former is monotonically increasing when new commits inherit from previous ones, and the latter can give a clue to lookup the commit from its hash in the commit log.'
	subparser = subparsers.add_parser(COMMAND_BUILDVERSION, help=help)
	subparser.add_argument('-0', '--raw', dest='raw', action='store_true', help=raw_option_help)

	#group.add_argument('-l', '--list', dest='list', action='store_true', help='Lists all project dependencies, as declared in the %s file.' % (GLUEDEPS_FILENAME))

	args = parser.parse_args(argv[1:])

	project = Project()

	#deps = project.dependencies # type: list[Dependency]

	logging.info("Loaded dependencies: %s", project.dependencies)

	# print("command -> " + args.command)

	try:
		if args.command == COMMAND_LIST:
			logging.debug("listing deps")
			print("Dependencies:")
			for dep in project.dependencies:
				print("\t%s" % dep)
		elif args.command == COMMAND_STATUS:
			logging.debug("get dependency status")
			project.failIfMissingDependencies()
			print("Fetching…")
			if args.remote:
				for dep in project.dependencies:
					dep.fetch()
					sys.stdout.write(dep.name + " ")
					sys.stdout.flush()
				
			for dep in project.dependencies:
				uncommitted = dep.hasUncommittedChanges()
				remoteStatus = ""
				if args.remote:
					s = dep.getRemoteChanges()
					if s[0] > 0 or s[1] > 0:
						remoteStatus = "%d"%s[0] + style.cyan("↑")+ " %d"%s[1] + style.cyan("↓")
				# rev = 'uncommitted' if uncommitted else dep.getRevision()
				print("%s (at %s/, type=%s):" % (style.dependency(dep.name), dep.path, dep.type))
				print("\tstatus: %s %s" % ( style.error('uncommitted') if uncommitted else style.ok('clean') , remoteStatus))
				print("\tcurrent branch: %s" % (style.branch(dep.getCurrentBranch())))
				print("\trevision: %s" % (style.revision(dep.getRevision())))
		elif args.command == COMMAND_ADVANCE:
			logging.debug("advancing deps: %s" % ", ".join(args.deps))
			project.failIfMissingDependencies()
		elif args.command == COMMAND_RECORD:
			logging.debug("recording revisions for dependencies")
			project.failIfMissingDependencies()
			project.recordDepsStates()
		elif args.command == COMMAND_UPDATE:
			logging.debug("updating dependencies (clean: %d)" % (args.clean))
			# update main project if requested (and its states file)
			project.failIfMissingDependencies()
			project.failIfUncommittedDependencies()

			# read states
			states = project.loadStates()

			print("states: " + states)
			# update dependencies
			# project.updateDependencies(states)
		elif args.command == COMMAND_CHECK:
			logging.debug("checking deps")
			# project.failIfUncommittedDependencies()
			project.failIfMissingDependencies()
			uncommittedDeps = project.uncommittedDependencies()
			if uncommittedDeps: # python's way to test not empty
				uncString = ", ".join(dep.name for dep in uncommittedDeps)
				outFormat = "%s" if args.raw else "Check failed. The following dependencies have uncommitted changes:\n\t%s"
				print(outFormat % uncString)
				sys.exit(1)
			else:
				if not args.raw:
					print("All dependencies are committed")
		elif args.command == COMMAND_BUILDVERSION:
			logging.debug("generate build version")
			project.failIfMissingDependencies()
			# project.failIfUncommittedDependencies()
			interface = project.interface()
			dirty = project.hasUncommittedDependencies()
			suffix = ".1" if dirty else ""
			buildversion = interface.getBuildNumberString()+suffix

			# print("Build version: %s" % interface.getBuildNumberString())
			if args.raw:
				print("%s" % buildversion)
			else:
				fbuildversion = style.warning(buildversion)+" (uncommitted changed)" if dirty else style.ok(buildversion)
				print("Build Version: %s" % fbuildversion)
		else:
			raiseError("Unrecognized command '%s'" % " ".join(argv[1:]))

	except Exception as e:
		print(e.message)
		return sys.exit(1)

		# uncommittedDeps = project.uncommittedDependencies()
		# if len(uncommittedDeps) > 0:
		# 	print("Aborting. The following dependencies have uncommitted changes:\n\t%s" %
		# 		  ", ".join(dep.name for dep in uncommittedDeps))
		# states = {}
		# statesString = ""
		# for dep in project.dependencies:
		# 	state = dep.getState()
		# 	# states[dep.name] =
		# 	statesString += dep.name + ": " + hjson.dumps(state, indent="\t") + "\n"
		#
		# # print "HJSON: " + hjson.dumps(states, indent="\t")
		# #print "States contents: " + statesString


	# text = """{
  	# 	foo: a
  	# 	bar: 1
	# 	}"""
	# parsed = hjson.loads(text)
	# logging.debug("parsed: %s" % parsed)



if __name__=='__main__':
	main(sys.argv)

