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

import ConfigParser
import os

CONFIG_FILE = "/opt/tct/shell/CONFIG"

parser = ConfigParser.ConfigParser()
parser.read(CONFIG_FILE)

class Constants:

     TEST_SUITE_DIR  = parser.get('TCTSHELL', 'TEST_SUITE_DIR')

     WRT_LAUNCHR_CMD = parser.get('TCTSHELL', 'WRT_LAUNCHR_CMD')

     RELEASED_SUITE_LOCATION = TEST_SUITE_DIR + "%s"

     TESTKIT_SHELL_HOME = parser.get('TCTSHELL', 'TCT_SHELL_HOME')

     TEMP_UNPASSED_XML_FOLDER = TESTKIT_SHELL_HOME + "/tmp/"

     TEMP_RESULT_XML_FOLDER = TESTKIT_SHELL_HOME + "/result/"

     if not TEMP_UNPASSED_XML_FOLDER.endswith('/'):
            TEMP_UNPASSED_XML_FOLDER = TEMP_UNPASSED_XML_FOLDER + "/"
     
     RERUN_OUTPUT = " -o " + TEMP_UNPASSED_XML_FOLDER + "result.xml"

     CAPABILITY_SUITE_NAME = "capability-tests"

     TCT_PLAN_FOLDER = parser.get('TCTSHELL', 'TCT_PLAN_FOLDER')

     STYLE_FOLDER = "/opt/tct/shell/style/*"

     CAPABILITY_PATH = "/opt/tct/shell/tmp/capability.xml"

     DEVICE_CAPABILITY_PATH = "/opt/usr/media/Documents/tct/capability.xml"

     #PARAM Option
     XMLFILE_PREFF = "-f device:"
     EXECUTE_PREFF = " -e "
     SKIP_NATIVE_MANUAL = "--non-active"
     ONLY_AUTO_CASES = "-A"
     ONLY_MANUAL_CASES = "-M"
     
     #SDB Command
     SDB_PUSH = "sdb push"
     SDB_SHELL = "sdb shell"
     SDB_DEVICES = "sdb devices"
     SDB_PULL = "sdb %s pull"

     
     #DEVICE
     DEVICE_TMP_FOLDER = parser.get('Device', 'DEVICE_TMP_FOLDER')
     DEVICE_TESTS_FILE = parser.get('Device', 'DEVICE_TESTS_FILE') + " "

     INSTALL_RPM       = "rpm -i --nodeps /tmp/%s"
     UNINSTALL_RPM     = "rpm -e --nodeps %s"

     #Plan Generator
     DEFAULT_MATCH_REGEX = "*.rpm"
     DEFAULT_UNMATCH_REGEX = None
     
     REGEX_FOR_SPLIT_PKG_NAME = "-\d\.\d\.\d"

     #Running Mode
     RUNNING_MODE_PLAN = "plan"
     RUNNING_MODE_RESULT = "result"
     RUNNING_MODE_SUITES = "suites"

     @staticmethod
     def add_right_enbrace(param):
         param = param.rstrip()
         param += "\""
         return param

     @staticmethod
     def indent(elem, level=0):
         i = "\n" + level*"  "
         if len(elem):
             if not elem.text or not elem.text.strip():
                 elem.text = i + "  "
             if not elem.tail or not elem.tail.strip():
                 elem.tail = i
             for elem in elem:
                 Constants.indent(elem, level+1)
             if not elem.tail or not elem.tail.strip():
                 elem.tail = i
         else:
             if level and (not elem.tail or not elem.tail.strip()):
                 elem.tail = i

     @staticmethod
     def copy_style_in_result_folder(result_folder):
         os.system("cp -r " + Constants.STYLE_FOLDER + " '" + result_folder + "'")
         print "Going to open the result report with FireFox, if Firefox is not available on your machine, please copy the folder '%s' to a Firefox machine." % result_folder
         os.system("firefox '%s'summary.xml &" % result_folder)


