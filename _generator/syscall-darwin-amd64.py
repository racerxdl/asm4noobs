#!/usr/bin/env python3
import urllib.request 
import urllib.parse 
import json
import base64
import re
import os

from urllib.request import urlopen
from pycparser import c_parser, c_ast


URL = "https://raw.githubusercontent.com/apple/darwin-xnu/main/bsd/kern/syscalls.master"
argRegs = [ "rdi", 'rsi', 'rdx', 'r10', 'r8', 'r9' ]

print("Loading syscall table from %s" % URL)
with urlopen(URL) as f:
	systbl = f.read().decode('utf-8')

ELSEIF_REGEX = r'#if (.*?)\n(.*?)#else(.*?)#endif'

elifregex = re.compile(ELSEIF_REGEX, flags=re.S)

p = elifregex.findall(systbl)
elifParts = []

for i in p:
	cond, iftrue, iffalse = i
	elifParts.append({
		"cond": cond,
		"iftrue": iftrue,
		"iffalse": iffalse,
	})
	systbl = systbl.replace("#if %s\n%s#else%s#endif" % (cond, iftrue, iffalse), "")
	systbl = systbl + "\n" + iftrue

if len(elifregex.findall(systbl)) > 0:
	print("Something went wrong!")

systbl = [ line.strip() for line in systbl.split("\n")]
systbl = filter(None, systbl)
systbl = filter(lambda line: line[0] != "#", systbl)
systbl = filter(lambda line: line[0] != ";", systbl)
systbl = filter(lambda line: line[0] != "/", systbl)
systbl = [ line.replace("\t", " ").strip() for line in systbl]

funcreg = re.compile(r'(.*?)\((.*?)\)')
funcfilter = re.compile(r'{(.*?)}')

syscallData = {
	"os": "darwin",
	"arch": "amd64",
	"argRegs": argRegs,
	"syscalls": [],
	"byName" : {}
}

for entry in systbl:
	id, audit, files, func = entry.split(None, 3)
	func = funcfilter.findall(func)[0].strip()
	matches = funcreg.match(func)
	funcNameRet = matches.group(1)
	funcArgs = matches.group(2).split(",")
	print("Name: %s Args: %s" % (funcNameRet, funcArgs))
	funcName = funcNameRet.split(" ")[-1:][0]
	retType = funcNameRet[:-len(funcName)].strip()
	syscall = {
		"name": funcName,
		"id": id,
		"audit": audit,
		"files": files,
		"filename": "unknown",
		"returnType": retType,
		"args": []
	}
	i = 0
	for arg in funcArgs:
		argName = arg.split(" ")[-1:][0]
		argType = arg[:-len(argName)].strip()
		syscall["args"].append({
            "name": argName,
            "type": argType,
            "idx": i,
            "reg": argRegs[i] if i < len(argRegs) else "STACK"
		})
		i += 1
	if not "nosys" in funcName:
		syscallData["syscalls"].append(syscall)
		syscallData["byName"][funcName] = syscall


with open("syscalls_darwin_amd64.json", "w") as f:
	f.write(json.dumps(syscallData, indent=4))

with open("_data/syscalls_darwin_amd64.json", "w") as f:
	f.write(json.dumps(syscallData, indent=4))