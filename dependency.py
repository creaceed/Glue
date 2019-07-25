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
