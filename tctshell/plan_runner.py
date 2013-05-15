#!/usr/bin/python
#
# Copyright (C) 2012 Intel Corporation
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:
#              Tang, Shaofeng <shaofeng.tang@intel.com>

from constants import Constants
from xml.etree import ElementTree
import os
import glob
import re

class SuitePackage:
    def __init__(self, file_name, command):
        m = re.split(Constants.REGEX_FOR_SPLIT_PKG_NAME, file_name)
        self.name = m[0]
        self.command = command + " %s" % self.name

    def to_xml(self):
        suite = ElementTree.Element('suite')
        suite.set('name', self.name)
        command = ElementTree.Element('command')
        command.text = self.command
        suite.append(command)
        return suite

class PlanRunner:

    def __init__(self):
        self.suites = {}

    def load_local_repo(self, path, match, command, unmatch):
        try:
            os.chdir(path)
            print "match: %s" % match
            print "unmatch: %s" % unmatch
            for files in glob.glob(match):
                print "File name: %s" % str(files)
                if (unmatch is not None) and (re.search(unmatch, str(files))):
                    print "File %s is skipped with unmatch regex %s" % (str(files), unmatch)
                else:
                    suite = SuitePackage(files, command)
                    self.suites[suite.name] = suite
        except Exception, e:
            print "[ Error happen when reading the local repository, error: %s ]\n" % e

    def to_xml(self, xml_name):
        print "generating plan to %s" % xml_name
        root = ElementTree.Element('testplan')
        for suite_name in self.suites:
            suite = self.suites[suite_name]
            root.append(suite.to_xml())
        Constants.indent(root)
        tree = ElementTree.ElementTree()
        tree._setroot(root)
        tree.write(xml_name, encoding="utf-8")
