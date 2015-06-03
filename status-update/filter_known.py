#!/bin/python

from __future__ import print_function

import zipfile
import csv
import os.path
import math
import sys
import xml.etree.ElementTree as etree

def starExecZipToSpaceXml(xml_zip_filename, xml_filename):
    assert zipfile.is_zipfile(xml_zip_filename)
    zf = zipfile.ZipFile(xml_zip_filename, 'r')
    spacexml = None
    try:
        data = zf.open(xml_filename)
        spacexml = etree.parse(data)
    finally:
        zf.close()
    return rows

spaceName = "2015-06-01"
spacexml = starExecZipToSpaceXml(spaceName + "_XML.zip",
                                 spaceName + "_XML/"+ spaceName + ".xml")
