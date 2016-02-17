#!/usr/bin/env python

import argparse
from Config import conf
import os
from os import listdir
from os.path import isdir, isfile, join
import json

def initParser():
    parser = argparse.ArgumentParser(description='Generate the results file for the exhaustive exploration.')
    parser.add_argument('-version', default=conf.defaultResultsVersion, required=False, help='The version of the results')
    return parser.parse_args()

args = initParser()

path = join(conf.resultsFolder, args.version, "exhaustive_exploration")

output = {}

projects = [f for f in listdir(path) if isdir(join(path, f))]
for project in projects:
	projectOutput = {}
	versions = [f for f in listdir(join(path, project)) if isfile(join(join(path, project), f))]
	for version in sorted(versions, reverse=True):
		executionPath = join(path, project, version)
		with open(executionPath) as data_file:
			resultsData = (json.load(data_file))
			output[project] = int(version.replace(".json", ""))
			print executionPath
		break
f = open(join(path, "results.json"), "w")
f.write(json.dumps(output, indent=2, sort_keys=True))