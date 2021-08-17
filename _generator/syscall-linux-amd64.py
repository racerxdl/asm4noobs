#!/usr/bin/env python3
import urllib.request 
import urllib.parse 
import json
import base64
import re
import os

from urllib.request import urlopen

SYSCALL_DEFINE_REGEX = r'SYSCALL_DEFINE[0-9]\(.*?\)'
SYSCALL_ARG_GROUP = r'\((.*?)\)'

CODEAPI = "https://api.github.com/search/code"
URL = "https://raw.githubusercontent.com/torvalds/linux/master/arch/x86/entry/syscalls/syscall_64.tbl"

global resourceCache
global headers

resourceCache = {}
argRegs = [ "rdi", 'rsi', 'rdx', 'r10', 'r8', 'r9' ]

headers = {}

if os.environ["GH_READ_TOKEN"]:
	headers["Authorization"] = "bearer %s" % os.environ["GH_READ_TOKEN"]
else:
	print("No Github Personal Access Token defined in ENV GH_READ_TOKEN. You might get rate limit")

def saveCache():
	global resourceCache
	with open("resource.cache", "w") as f:
		f.write(json.dumps(resourceCache))

def getSyscalls(content):
	content = base64.b64decode(content).decode("utf-8")
	return re.findall(SYSCALL_DEFINE_REGEX, content.replace("\n", "").replace("\t", " "))

def getCodeLine(objectUrl):
	global resourceCache
	global headers
	if objectUrl in resourceCache:
		# print("Loaded object from cache %s" % objectUrl)
		data = resourceCache[objectUrl]
	else:
		print("Fetching %s" % objectUrl)
		req = urllib.request.Request(objectUrl, headers=headers)
		with urlopen(req) as f:
			data = json.loads(f.read().decode('utf-8'))
		resourceCache[objectUrl] = data
		saveCache()

	data = data["content"]
	return getSyscalls(data)

def getCodeFilename(objectUrl):
	global resourceCache
	global headers
	if objectUrl in resourceCache:
		# print("Loaded object from cache %s" % objectUrl)
		data = resourceCache[objectUrl]
	else:
		print("Fetching %s" % objectUrl)
		req = urllib.request.Request(objectUrl, headers=headers)
		with urlopen(req) as f:
			data = json.loads(f.read().decode('utf-8'))
		resourceCache[objectUrl] = data
		saveCache()

	return data["path"]

def parseSyscallEntry(entry):
	entry = entry.replace("\n", " ")
	results = re.findall(SYSCALL_ARG_GROUP, entry)
	if len(results) != 1:
		return None
	sysname, *args = results[0].split(",")
	syscall = { "name": sysname, "args": [], "variadic": False }
	if len(args) == 1 and args[0].strip() == "...":
		syscall["variadic"] = True
	elif len(args) % 2 != 0:
		print("WARN, ARGS maybe wrong: %s" % args)
	else:
		for i in range(int(len(args) / 2)):
			type = args[i*2].strip()
			name = args[i*2+1].strip()
			syscall["args"].append({"name": name, "type": type, "idx": i, "reg": argRegs[i] })

	return syscall

def loadSyscallDefineN(n):
	global resourceCache
	global headers

	params = { 
	    "q": "in:file language:c repo:torvalds/linux SYSCALL_DEFINE%d" % n,
	}    
	 
	query_string = urllib.parse.urlencode( params )
	url = CODEAPI + "?" + query_string

	if url in resourceCache:
		searchres = resourceCache[url]
	else:
		req = urllib.request.Request(url, headers={ **headers, "Accept": "application/vnd.github.v3.text-match+json" })
		with urlopen(req) as f:
			searchres = json.loads(f.read().decode('utf-8'))
		resourceCache[url] = searchres
		saveCache()

	if searchres["total_count"] > 0:
		for item in searchres["items"]:
			textMatch = item["text_matches"]
			for match in textMatch:
				for submatch in match["matches"]:
					syscallMatches = getCodeLine(match["object_url"])
					filename = getCodeFilename(match["object_url"])
					for sm in syscallMatches:
						syscallDefines.append({
							"define": sm,
							"filename": filename
						})

try:
	print("Loading resource cache")
	with open("resource.cache", "r") as f:
		resourceCache = json.loads(f.read())
except Exception as e:
	print("Error loading cache: %s" % e)
	pass

print("Loading syscall table from %s" % URL)
with urlopen(URL) as f:
	systbl = f.read().decode('utf-8')

systbl = systbl.split("\n")

syscalls = []

for line in systbl:
	line = line.strip()
	if len(line) > 0 and line[0] != "#":
		sysdata = line.split()
		if len(sysdata) != 0:
			sysnum, arch, name, *rest = sysdata
			entry = None
			if len(sysdata) == 4:
				entry = sysdata[3]
			if arch == "common" or arch == "64":
				syscalls.append({
					"id": int(sysnum),
					"name": name,
					"entry": entry,
				})



print("There are %d entries in cache" % len(resourceCache))

sysdata = syscalls[0]
syscallDefines = []

for i in range(7):
	print("Loading syscall defines for %d arguments" % i)
	loadSyscallDefineN(i)

newDefines = []
definesByName = {
	"global": {},
}

for entry in syscallDefines:
	parsed = parseSyscallEntry(entry["define"])
	if parsed != None:
		entry["name"] = parsed["name"]
		entry["args"] = parsed["args"]
		newDefines.append(entry)
		if "arch" in entry["filename"]:
			arch = entry["filename"].split("/")[1]
		else:
			arch = "global"
		if not arch in definesByName:
			definesByName[arch] = {}

		definesByName[arch][entry["name"]] = entry


with open("_generator/syscall_linux_amd64.defines", "w") as f:
	f.write(json.dumps(newDefines, indent=4))
with open("_generator/syscall_linux_amd64_ByName.defines", "w") as f:
	f.write(json.dumps(definesByName, indent=4))

syscallData = {
	"os": "linux",
	"arch": "amd64",
	"argRegs": argRegs,
	"syscalls": [],
	"byName" : {}
}

for sys in syscalls:
	# AMD64 is x86
	if sys["name"] in definesByName["global"]:
		data = definesByName["global"][sys["name"]]
	elif sys["name"] in definesByName["x86"]:
		data = definesByName["x86"][sys["name"]]
	else:
		data = None

	if data != None:
		sys["args"] = data["args"]
		sys["filename"] = data["filename"]
	syscallData["syscalls"].append(sys)
	syscallData["byName"][sys["name"]] = sys


with open("syscalls_linux_amd64.json", "w") as f:
	f.write(json.dumps(syscallData, indent=4))

with open("_data/syscalls_linux_amd64.json", "w") as f:
	f.write(json.dumps(syscallData, indent=4))