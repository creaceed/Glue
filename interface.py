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

import shlex
import subprocess
import logging
import os

GIT_BINARY = "/usr/bin/git"
HG_BINARY = "/usr/local/bin/hg"

class VersioningSystemInterface:
	def __init__(self, path, url):
		self.executable = None
		self.path = path
		self.url = url
		# os.path.isdir()
	@staticmethod
	def interface(path):
		if os.path.isdir(os.path.join(path, ".git")):
			return GitInterface(path, "")
		elif os.path.isdir(os.path.join(path, ".hg")):
			return MercurialInterface(path, "")
		else:
			return None
	def executeCommand(self, args): # "%s %s" % (GitInterface.GIT_PATH, args)
		sargs = [self.executable] + shlex.split(args)
		pro = subprocess.Popen(sargs, cwd = self.path, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		(out, error) = pro.communicate()
		ret = pro.returncode
		if ret != 0 > 0:
			logging.error("Error %d while executing command '%s'" % (ret, " ".join(sargs)))
			raise StandardError(error)

		return out.decode()
	def exists(self):
		raise NotImplementedError
	def fetch(self):
		raise NotImplementedError
	def hasUncommittedChanges(self):
		raise NotImplementedError
	def getRemoteChanges(self):
		raise NotImplementedError
	def getRevisionCount(self):
		raise NotImplementedError
	def getRevision(self):
		raise NotImplementedError
	def getBuildNumberString(self):
		rev = self.getRevision()
		c = self.getRevisionCount()
		# logging.debug("Revision=%s Count=%d" % (rev, c))
		# first number: commit count since repository start. 
		# second number: decimal version of the number made of first 3 hexchar of hash.
		return "%d.%d" % (c, int(rev[0:3], 16))
	def getDate(self):
		raise NotImplementedError
	def getCurrentBranch(self):
		raise NotImplementedError
	def updateToRevision(self, revision):
		raise NotImplementedError

class GitInterface(VersioningSystemInterface):
	def __init__(self, path, url):
		VersioningSystemInterface.__init__(self, path, url)
		self.executable = GIT_BINARY
	def exists(self):
		return os.path.isdir(os.path.join(self.path, ".git"))
	def fetch(self):
		self.executeCommand("fetch")
	def hasUncommittedChanges(self):
		out = self.executeCommand("status -s")
		lines = str.splitlines(out)
		return len(lines) > 0
	def getRemoteChanges(self):
		up = self.getRevisionCountRange(range="@{u}..")
		down = self.getRevisionCountRange(range="..@{u}")
		return (up,down)
	def getRevision(self):
		return self.executeCommand("log --pretty=format:'%H' -n 1")
	def getRevisionCountRange(self, range): 
		val = self.executeCommand("rev-list --count %s" % range)
		return int(val) if val != '' else 0
	def getRevisionCount(self): 
		return self.getRevisionCountRange(range="HEAD")
	def getDate(self):
		return self.executeCommand("log --pretty=format:'%ci' -n 1")
	def getCurrentBranch(self):
		b = self.executeCommand("rev-parse --abbrev-ref HEAD")
		b = b.strip()
		return b
	def updateToRevision(self, revision):
		self.executeCommand("checkout %s" % revision)

class MercurialInterface(VersioningSystemInterface):
	def __init__(self, path, url):
		VersioningSystemInterface.__init__(self, path, url)
		self.executable = HG_BINARY
		# self.getRevisionCount()
		# print("rev count: %d" % self.getRevisionCount())
	def exists(self):
		return os.path.isdir(os.path.join(self.path, ".hg"))
	def hasUncommittedChanges(self):
		out = self.executeCommand("status")
		lines = str.splitlines(out)
		return len(lines) > 0
	# def getRemoteChanges(self):
	# 	return (0,0)
	def getRevision(self):
		return self.executeCommand("parent --template '{node}'")
	def getRevisionCount(self): 
		rev = self.getRevision()
		lines = self.executeCommand("log -r '0::%s' --template '{node}\n'" % rev)
		count = lines.count('\n')
		# print("lines: %d" % lines.count('\n'))
		return count
	def getDate(self):
		return self.executeCommand("parent --template '{date|isodatesec}'")
	def getCurrentBranch(self):
		return self.executeCommand("parent --template '{branch}'")
	def updateToRevision(self, revision):
		self.executeCommand("update -c --rev %s" % revision)
