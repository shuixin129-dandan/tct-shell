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


import os
import re
import sys, traceback
import time
import platform
import ctypes
import glob
import ConfigParser
import xml.etree.ElementTree as etree
from optparse import *
from shutil import copyfile
from tempfile import mktemp
from datetime import datetime
from constants import Constants

#show all available suites
def show_available_suites(option, opt_str, value, parser):
    if platform.system() != "Linux":
        Constants.TEST_SUITE_DIR = "../suites"
    print "Test Suites:...\n"
    os.chdir(Constants.TEST_SUITE_DIR)
    for files in glob.glob("*.rpm"):
        #without ".rpm"
        print files[:-4]
    sys.exit(1) 

def print_planfolder(option, opt_str, value, parser):
    print "Plan folder: %s" % Constants.TCT_PLAN_FOLDER
    os.system("tree %s" % Constants.TCT_PLAN_FOLDER)
    sys.exit(1)

def varnarg(option, opt_str, value, parser):
    """ parser srg"""
    value = []
    import re
    for arg in parser.rargs:
        if re.search('^--.+', arg) or re.search('^-[\D]', arg):
            break
        value.append(arg)

    del parser.rargs[:len(value)]
    setattr(parser.values, option.dest, value)

class PlanGeneratorOptions:

     def __init__(self):
         print ""
         self._j = os.path.join
         self._e = os.path.exists
         self._d = os.path.dirname
         self._b = os.path.basename
         self._abspath = os.path.abspath
         self.testkit_dir = "/opt/testkit/lite"
         self.LOG_DIR = self.testkit_dir
         self.PID_FILE = self._j(self.LOG_DIR , "pid.log")
         if not platform.system() == "Linux":
             self.testkit_dir = self._d(self._abspath(__file__))
             sys.path += [self._j(self.testkit_dir)]
             self.testkit_dir = self._j(self.testkit_dir , "results")
         #self.clean_context()
         self.options = None
         self.options = None
         self.running_mode = None # plan suite result
         self.USAGE = "tct-plan-generator [options] --output <somewhere/testplan.xml>\n\
examples: \n\
          tct-plan-generator  -o  <somewhere>/testplan.xml\n\
          tct-plan-generator  -o  <somewhere>/testplan.xml -r <somewhere>/repository_folder\n\
          tct-plan-generator  -o  <somewhere>/testplan.xml -r <somewhere>/repository_folder --match '<regex>'\n\
\n\
    generate a test plan to include all suites in the local repository: \n\
          tct-plan-generator  -o  <somewhere>/testplan.xml\n\
    generate a test plan to include all suites in the special repository: \n\
          tct-plan-generator  -o  <somewhere>/testplan.xml -r <somewhere>/repository_folder\n\
    generate a test plan to include the suites in the special repository which name is matched with 'webapi*.rpm': \n\
          tct-plan-generator  -o  <somewhere>/testplan.xml -r <somewhere>/repository_folder  --match 'webapi*.rpm'\n\
    generate a test plan to include the suites in the special repository which name is matched with 'webapi*.rpm', and exclude the file 'webapi-tizen-push-tests-2.1.6-1.1.armv7l.rpm': \n\
          tct-plan-generator  -o  <somewhere>/testplan.xml -r <somewhere>/repository_folder  --match 'webapi*.rpm' --unmatch push\n\
\n\
Note: \n\
          1) run command 'tct-plan-generator', it might not be able to locate related module, run command 'export PYTHONPATH=/usr/lib/python2.7/site-packages' to resolve this issue"

     
     def print_usage(self):
         print self.USAGE

     def parse_options(self, argv):
         option_list = [
                    make_option("-o", "--output", dest="testplan_file",
                                action="callback", callback=varnarg,
                                help="Specify the generating testplan in a XML file."),
                    make_option("-r", "--repository", dest="repository_folder",
                                action="callback", callback=varnarg,
                                help="Specify the path of local repository."),
                    make_option("-m", "--match", dest="match_regex",
                                action="callback", callback=varnarg,
                                help="The regex for matching filename."),
                    make_option("-u", "--unmatch", dest="unmatch_regex",
                                action="callback", callback=varnarg,
                                help="The regex for unmatching filename."),
                    make_option("--plan-list", dest="show_plan_folder", 
                                action="callback", callback=print_planfolder, 
                                help="List all existed plan in the Plan folder. \
                                The plan folder is defined in the configure '/opt/testkit/shell/CONF'"),
                    make_option("-a", "--all-suites", dest="show_suites", 
                                action="callback", callback=show_available_suites, 
                                help="Show all available test-suites"),
                    make_option("-c", "--command", dest="command", 
                                action="callback", callback=varnarg, 
                                help="The command which will be used to start a widget. \
                                Possible value: WRTLauncher, firefox, and/or other browser with appropriate parameters.\
                                By default, the command is 'WRTLauncher'"),
                  ]
         # detect non-params
         if len(argv) == 1:
             argv.append("-h")
         PARSERS = OptionParser(option_list=option_list, usage=self.USAGE)
         (self.options, args) = PARSERS.parse_args()

     def get_repository_folder(self):
         if (self.options.repository_folder is not None) and (self.options.repository_folder[0] is not None):
             return self.options.repository_folder[0]
         else:
             return Constants.TEST_SUITE_DIR

     def get_match_regex(self):
         if (self.options.match_regex is not None) and (self.options.match_regex[0] is not None):
             return self.options.match_regex[0]
         else:
             return Constants.DEFAULT_MATCH_REGEX

     def get_command(self):
         if (self.options.command is not None) and (self.options.command[0] is not None):
             return self.options.command[0]
         else:
             return Constants.WRT_LAUNCHR_CMD

     def get_output(self):
         if (self.options.testplan_file is not None) and (self.options.testplan_file[0] is not None):
             d = os.path.abspath(os.path.dirname(self.options.testplan_file[0]))
             if not os.path.exists(d):
                 os.makedirs(d)
             return os.path.abspath(self.options.testplan_file[0])
         else:
             return Constants.TCT_PLAN_FOLDER + "generated_plan.xml"

     def get_unmatch_regex(self):
         if (self.options.unmatch_regex is not None) and (self.options.unmatch_regex[0] is not None):
             return self.options.unmatch_regex[0]
         else:
             return Constants.DEFAULT_UNMATCH_REGEX
