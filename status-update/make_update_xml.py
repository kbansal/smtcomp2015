#!/usr/bin/env python

from __future__ import print_function

import zipfile
import csv
import os.path
import math
import sys
import xml.etree.ElementTree as etree

#LOG_CORRECT = "process_fornextstep.txt"
#INPUT_XML="raw/non-incremental.xml"

LOG_CORRECT = "test.txt"
INPUT_XML="test.xml"
#INPUT_XML="update_subset.xml"

spacexml = etree.parse(INPUT_XML)

for line in open(LOG_CORRECT):
    bench, ans = line.split(', ')
    bench, ans = bench.strip(), ans.strip()
    dirs = ['non-incremental'] + bench.split('/')[:-1]
    filename = bench.split('/')[-1]
    # print(dirs, filename, ans)
    nodes = spacexml.findall("./Space[@name='"+"']/Space[@name='".join(dirs)+"']"+
                            "/Benchmark[@name='"+filename+"']")
    if len(nodes) == 0:
        print("Error: " + bench + " not found in Space XML.", file=sys.stderr)
        continue
    elif len(nodes) == 1:
        node = nodes[0]
    else:
        print("Error: " + bench + " has too many entries ("+str(len(nodes))+").", file=sys.stderr)
        continue
    node.tag = 'Update'
    node.attrib['bid']='83'
    node.attrib['pid']='183'
    subnode = etree.Element(tag='Text',attrib={})
    subnode.text=ans
    node.append(subnode)
    # print(node.tag)
    # print(node.attrib)
    # print(node.text)
    # etree.dump(node)

# space nodes, reorder according to:
#  "our schema requires that each
#   Space element has these elements in this order:
#   0 or 1 SpaceAttribute elements
#   0 or more Update elements
#   0 or more Benchmark elements
#   0 or more Solver elements
#   0 or more Space elements."
spacenodes = spacexml.findall(".//Space")
for spacenode in spacenodes:
    updateChildren = [x for x in spacenode if x.tag == "Update"]
    numSpaceAttribtes = len([x for x in spacenode if x.tag == "SpaceAttributes"])
    for c in updateChildren:
        spacenode.remove(c)
        spacenode.insert(numSpaceAttribtes, c)

etree.dump(spacexml)
