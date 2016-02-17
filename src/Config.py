import os
from os.path import expanduser

class Config(object):
	def __init__(self):
		self.defaultResultsVersion = "2016-February"
		self.resultsFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "results")

conf = Config()
