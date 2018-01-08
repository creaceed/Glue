import os
import logging
import hjson

from common import *
from dependency import *

GLUEDEPS_FILENAME = ".gluedeps"
GLUESTATES_FILENAME = ".gluestates"

# Main project, the one holding deps / states files.
class Project:
	def __init__(self, path="."):
		logging.debug("project init")
		self.path = path
		self.dependencies = self.loadDeps() # type: list[Dependency]

	def getSortedDependencies(self):
		return sorted(self.dependencies, key=lambda dep: dep.name.lower())

	def interface(self):
		return VersioningSystemInterface.interface(self.path) # no url, not important here

	def pathForSubpath(self, subp):
		dir = self.path
		path = subp
		if dir:
			path = os.path.join(dir, path)
		return path

	def gluedepsPath(self):
		return self.pathForSubpath(GLUEDEPS_FILENAME)

	def gluestatesPath(self):
		return self.pathForSubpath(GLUESTATES_FILENAME)

	def failIfUncommittedDependencies(self):
		uncommittedDeps = self.uncommittedDependencies()
		if len(uncommittedDeps) > 0:
			raiseError("Aborting. The following dependencies have uncommitted changes:\n\t%s" % 
			", ".join(dep.name for dep in uncommittedDeps))
	def getStates(self):
		self.failIfUncommittedDependencies()
		states = {}

		for dep in self.dependencies:
			state = dep.getState()
			states[dep.name] = state
		return states

	def recordDepsStates(self):
		states = self.getStates()
		statesString = ""
		for dep in self.getSortedDependencies():
			state = states[dep.name]
			statesString += dep.name + ": " + hjson.dumps(state, indent="\t") + "\n"

		logging.info("Writing states to %s", self.gluestatesPath())
		f = open(self.gluestatesPath(), "w")
		# logging.info("Writing states: \n%s", statesString)
		f.write(statesString)
		f.close()

	def checkStates(self, states):
		for dep in self.dependencies:
			if dep.name not in states or STATE_REVISION not in states[dep.name]:
				raiseError("Incorrect/missing state for dependency %s" % (dep.name))

	def loadStates(self):
		f = open(self.gluestatesPath(), "r")
		statesString = f.read()
		logging.info("Reading states: \n%s", statesString)
		states = hjson.loads(statesString)
		logging.info("Read states: \n%s", states)
		f.close()
		self.checkStates(states)
		return states

	def loadDeps(self):
		dicts = hjson.load(file(self.gluedepsPath()))
		deps = []

		# logging.debug("loaded deps file: %s" % deps)
		for name, dict in dicts.items():
			try:
				dep = Dependency(name, dict)
			except Exception as e:
				dep = None
				logging.warn("Skipping dep %s: ", e)
				continue
			if dep is not None:
				# deps[name] = dep
				deps.append(dep)
		return deps

	def updateDependencies(self, states):
		for dep in self.dependencies:
			state = states[dep.name]
			if state == None:
				raiseError("Missing state for dependency %s" % (dep.name))
			dep.update(state)

	def fetchDependencies(self):
		for dep in self.dependencies:
			dep.fetch()

	def hasUncommittedDependencies(self):
		for dep in self.dependencies:
			# logging.debug("dep<%s>: uncommitted=%s" % (dep.name, dep.hasUncommittedChanges()))
			if dep.hasUncommittedChanges():
				return True
		return False
	def uncommittedDependencies(self):
		return [dep for dep in self.dependencies if dep.hasUncommittedChanges()]
