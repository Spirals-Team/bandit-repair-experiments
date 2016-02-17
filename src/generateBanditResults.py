#!/usr/bin/env python

import argparse
from Config import conf
import os
from os import listdir
from os.path import isdir, isfile, join
import json

def initParser():
    parser = argparse.ArgumentParser(description='Generate the results file for the bandit exploration.')
    parser.add_argument('-version', default=conf.defaultResultsVersion, required=False, help='The version of the results')
    return parser.parse_args()

args = initParser()

path = join(conf.resultsFolder, args.version, "bandit_exploration")
dirs = [f for f in listdir(path) if isdir(join(path, f))]
output = {}
projects = [f for f in listdir(path) if isdir(join(path, f))]
for project in projects:
	projectOutput = {}
	versions = [f for f in listdir(join(path, project)) if isfile(join(join(path, project), f))]
	for version in sorted(versions):
		executionPath = join(path, project, version)
		with open(executionPath) as data_file:

			resultsData = (json.load(data_file))
			seed = None
			epsilon = None
			if "executions"  in resultsData:
				if "metadata" in resultsData["executions"][0] and "seed" in resultsData["executions"][0]["metadata"]:
					seed = resultsData["executions"][0]["metadata"]["seed"]
				if "decisions" in resultsData["executions"][0]:
					for decision in resultsData["executions"][0]["decisions"]:
						if "epsilon" in decision:
							epsilon = decision["epsilon"]
							break
			else:
				continue
			if seed is None or epsilon is None:
				continue
			if epsilon not in projectOutput:
				projectOutput[epsilon] = {}
			projectOutput[epsilon][seed] = int(version.replace(".json", ""))
			print executionPath
	output[project] = projectOutput
f = open(join(path, "results.json"), "w")
f.write(json.dumps(output, indent=2, sort_keys=True))