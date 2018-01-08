from interface import *


STATE_REVISION = "revision"
STATE_METADATE = "date"
# STATE_METABRANCH = "branch"

# Dependencies of the main project
class Dependency:
	KEY_PATH='path'
	KEY_TYPE='type'
	KEY_BRANCH='branch'
	KEY_URL='url'

	REQUIRED_KEYS=[KEY_PATH, KEY_TYPE, KEY_BRANCH, KEY_URL]

	@classmethod
	def checkKeys(cls, dict):
		missing = []
		for key in Dependency.REQUIRED_KEYS:
			if key not in dict:
				# logging.error("Dependency is missing key '%s'", key)
				missing.append(key)
				# return False
		return missing

	def __init__(self, name, dict):
		missing = Dependency.checkKeys(dict)
		if len(missing) > 0: raise Exception("Missing key(s): %s", missing)
		self.name = name
		self.path = dict[Dependency.KEY_PATH]
		self.type = dict[Dependency.KEY_TYPE]
		self.branch = dict[Dependency.KEY_BRANCH]
		self.url = dict[Dependency.KEY_URL]

		type = self.type
		interface = None
		if type == 'git':
			interface = GitInterface(self.path, self.url)
		elif type == 'hg':
			interface = MercurialInterface(self.path, self.url)
		self.interface = interface
	def __repr__(self):
		return '%s: path="%s" type=%s url="%s"' % (self.name, self.path, self.type, self.url)
	def fetch(self):
		self.interface.fetch()
	def hasUncommittedChanges(self):
		return self.interface.hasUncommittedChanges()
	def getRemoteChanges(self):
		return self.interface.getRemoteChanges()
	def getRevision(self):
		return self.interface.getRevision()
	def getCurrentBranch(self):
		return self.interface.getCurrentBranch()
	def getState(self):
		state = {}
		state[STATE_REVISION] = self.getRevision()
		state[STATE_METADATE] = self.interface.getDate()
		# not storing branch, misleading.
		#state[STATE_METABRANCH] = self.interface.getCurrentBranch()
		return state
	def update(self, state):
		revision = state[STATE_REVISION]
		self.interface.updateToRevision(revision)
