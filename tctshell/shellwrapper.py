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

# version option
def print_version(option, opt_str, value, parser):
    try:
        CONFIG = ConfigParser.ConfigParser()
        if platform.system() == "Linux":
            CONFIG.read('/opt/testkit/lite/VERSION')            
        else:
            VERSION_FILE = os.path.join(sys.path[0], 'VERSION')
            CONFIG.read(VERSION_FILE)
        VERSION = CONFIG.get('public_version', 'version')
        print "V%s" % VERSION
    except Exception, e:
        print "[ Error: fail to parse version info, error: %s ]\n" % e
    sys.exit(1)  

def print_planfolder(option, opt_str, value, parser):
    print "Plan folder: %s" % Constants.TCT_PLAN_FOLDER
    os.system("tree %s" % Constants.TCT_PLAN_FOLDER)
    sys.exit(1)

def print_resultfolder(option, opt_str, value, parser):
    print "Result folder: %s" % Constants.TEMP_RESULT_XML_FOLDER
    os.system("tree %s" % Constants.TEMP_RESULT_XML_FOLDER)
    sys.exit(1)

def invoke_sdb_devices(option, opt_str, value, parser):
    os.system(Constants.SDB_DEVICES)
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

class TestKitShellWrapper:

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
         self.USAGE = "tct-shell [options] --testplan <somewhere/testplan.plan>\n\
examples: \n\
          tct-shell  --test package1 package2 ... packageN\n\
          tct-shell  --rerun-fail '<somewhere>/test-result.xml' \n\
          tct-shell  --testplan  <somewhere>/testplan.xml --capability <somewhere>/capability_list\n\
\n\
    run a test plan: \n\
          tct-shell  --testplan  <somewhere>/testplan.xml --capability <somewhere>/capability_list -o /tmp/wekit-tests-result.xml ...\n\
    run some test packages: \n\
          tct-shell  --test package1 package2 ... packageN -o /tmp/wekit-tests-result.xml ...\n\
    rerun all unpassed test: \n\
          tct-shell  --rerun-fail '<somewhere>/test-result.xml' ...\n\
    show all existed testplan which is in the folder (configured in /opt/testkit/shell/CONFIG): \n\
          tct-shell  --plan-list\n\
    show all history result which is in the folder (configured in /opt/testkit/shell/CONFIG): \n\
          tct-shell  --result-list\n\
    show all connected devices: \n\
          tct-shell  --device-list\n\
\n\
Note: \n\
          1) Proxy settings should be disabled when execute webapi packages\n\
          2) run command 'tct-shell', it might not be able to locate related module, run command 'export PYTHONPATH=/usr/lib/python2.7/site-packages' to resolve this issue"

     
     def print_usage(self):
         print self.USAGE

     def parse_options(self, argv):
         option_list = [
                    make_option("-p", "--testplan", dest="testplan_file",
                                action="callback", callback=varnarg,
                                help="Specify the testplan.xml."),
                    make_option("-o", "--output", dest="resultfile",
                                help="Specify output file for result xml. If more than one testxml provided, results will be merged together to this output file"),
                    make_option("--enable-memory-collection", dest="enable_memory_collection", action="store_true",
                                help="Enable the ability to release memory when the free memory is less than 100M"),
                    make_option("-v", "--version", dest="version_info", action="callback", callback=print_version, 
                                help="Show version information"),
                    make_option("--auto-iu", dest="auto_install", action="store_true", help="Automatically install and uninstall suite packages"),
                    make_option("-a", "--all-suites", dest="show_suites", action="callback", callback=show_available_suites, 
                                help="Show all available test-suites in the local repository, the local repository is defined in the configure '/opt/testkit/shell/CONF'"),
                    make_option("-c", "--capability", dest="capability_file", action="callback", callback=varnarg, 
                                help="Specify the capability file."),
                    make_option("-t", "--test", dest="suites", action="callback", callback=varnarg, 
                                help="Specify testing suites. If more than one suites are provided, just list them all and separate with whitespace"),
                    make_option("-r", "--rerun-fail", dest="fail_result_xml", action="callback", callback=varnarg, 
                                help="Rerun all fail testcase according to the specified result XML."),
                    make_option(Constants.SKIP_NATIVE_MANUAL, dest="skip_core_memory", action="store_true",
                                help="Disable the ability to set the result of core manual cases from the console"),
                    make_option("--deviceid", dest="deviceid", action="callback", callback=varnarg, 
                                help="set sdb device serial information."),
                    make_option("--plan-list", dest="show_plan_folder", action="callback", callback=print_planfolder, 
                                help="List all existed plan in the Plan folder. The plan folder is defined in the configure '/opt/testkit/shell/CONF'"),
                    make_option("--result-list", dest="show_all_result", action="callback", callback=print_resultfolder, 
                                help="List all history results in the result folder. The result folder is defined in the configure '/opt/testkit/shell/CONF'"),
                    make_option("--device-list", dest="show_all_device", action="callback", callback=invoke_sdb_devices, 
                                help="List all connected devices. just same with 'sdb devices'"),
                    make_option("--auto", dest="only_auto", action="store_true", help="Only automatic test cases will be executed"),
                    make_option("--manual", dest="only_manual", action="store_true", help="Only manual test cases will be executed"),
                    make_option("--id", dest="testcase_id", action="callback", callback=varnarg, 
                                help="Specify to run a test case by id."),
                  ]
         # detect non-params
         if len(argv) == 1:
             argv.append("-h")
         PARSERS = OptionParser(option_list=option_list, usage=self.USAGE)
         (self.options, args) = PARSERS.parse_args()
         if self.is_testplan_mode():
             self.running_mode = "plan"
         elif self.options.fail_result_xml is not None:
             self.running_mode = "result"
         elif self.options.suites is not None:
             self.running_mode = "suites"

     def get_suite_param(self):
         param = Constants.XMLFILE_PREFF + "\""
         
         for suite_name in self.options.suites:
             param += "%s " % suite_name
         param = Constants.add_right_enbrace(param)

         param += Constants.EXECUTE_PREFF  + ("\" %s " % Constants.WRT_LAUNCHR_CMD)
         for e_name in self.options.suites:
             param += "%s " % e_name
         param = Constants.add_right_enbrace(param)
         return param

     def is_testplan_mode(self):
         return self.options.testplan_file is not None 

     def is_suite_mode(self):
         return self.options.suites is not None

     def is_fail_rerun_mode(self):
         return self.options.fail_result_xml is not None

     def get_plan_name(self):
         plan_name = ""
         if self.is_testplan_mode():
             plan_name = "Plan: %s" % self.options.testplan_file[0]
         elif self.is_suite_mode():
             plan_name = "Temporary plan to execute the suites: %s " % str(self.get_suites())
         elif self.is_fail_rerun_mode():
             plan_name = "Temporary plan to re-run all un-Passed testcases in the result_XML '%s' " %  self.options.fail_result_xml[0]
         return plan_name
  
     def is_auto_install(self):
         return self.options.auto_install

     def get_output_param(self):
         return "-o %s" % self.get_output_file_name()

     def get_output_file_name(self):
         output = ""
         if self.options.resultfile is not None:
             output = os.path.abspath(self.options.resultfile)
         else:
             output = Constants.TEMP_UNPASSED_XML_FOLDER + "result.xml"
         return output

     def get_memory_param(self):
         memory_param = ""
         if self.options.enable_memory_collection:
             memory_param = "--enable-memory-collection"
         return memory_param

     def get_skip_native_manual_cases_param(self):
         skip = ""
         if self.options.skip_core_memory:
             skip = Constants.SKIP_NATIVE_MANUAL
         return skip

     def get_deviceid_param(self):
         deviceid = ""
         if self.options.deviceid is not None:
             deviceid = " --deviceid %s" % self.options.deviceid[0]
         return deviceid

     def get_sdb_device_id_param(self):
         deviceid = ""
         if self.options.deviceid is not None:
             deviceid = " -s %s" % self.options.deviceid[0]
         return deviceid

     def get_capability_param(self):
         capability_file = ""
         if self.options.capability_file is not None:
             capability_file = " --capability %s" % self.options.capability_file[0]
         return capability_file 

     def get_auto_case_param(self):
         auto = ""
         if self.options.only_auto:
             auto = Constants.ONLY_AUTO_CASES
         return auto

     def get_manual_case_param(self):
         manual = ""
         if self.options.only_manual:
             manual = Constants.ONLY_MANUAL_CASES
         return manual

     def get_testcase_id(self):
         tc_id = ""
         if self.options.testcase_id is not None:
             tc_id = " --id %s" % self.options.testcase_id[0]
         return tc_id
     
     def print_result_summary(self, result_file):         
         try:
             tree = etree.parse(result_file)
             root = tree.getroot()
             suites = root.findall('suite')
             
             total_cases = len(root.findall('suite/set/testcase'))
             #TODO below info should be replace by the summary obj
             print "[Result: execute %d suites]" % len(suites)
             print "[  total case number: %d ]" % total_cases
             if total_cases > 0:
                 print "[    Pass Rate: %d" % int(len(root.findall('suite/set/testcase[@result="PASS"]')) * 100 /total_cases) + "% ]"
             else:
                 print "[    Pass Rate: 0% ]"
             print "[    PASS case number: %d ]" % len(root.findall('suite/set/testcase[@result="PASS"]'))
             print "[    FAIL case number: %d ]" % len(root.findall('suite/set/testcase[@result="FAIL"]'))
             print "[    BLOCK case number: %d ]" % len(root.findall('suite/set/testcase[@result="BLOCK"]'))
             print "[    N/A case number: %d ]" % len(root.findall('suite/set/testcase[@result="N/A"]'))
             for suite in suites:
                 print " Suite: %s" % suite.get("name")
                 suite_cases_number = len(suite.findall('set/testcase'))
                 print "      |---total case number: %d " % suite_cases_number
                 if suite_cases_number > 0 :
                     print "      |      |---Pass rate: %d" % int(len(suite.findall('set/testcase[@result="PASS"]')) * 100 /len(suite.findall('set/testcase'))) + "%"
                 else:
                     print "      |      |---Pass rate: 0%"
                 print "      |      |---PASS case number: %d " % len(suite.findall('set/testcase[@result="PASS"]'))
                 print "      |      |---FAIL case number: %d " % len(suite.findall('set/testcase[@result="FAIL"]'))
                 print "      |      |---BLOCK case number: %d " % len(suite.findall('set/testcase[@result="BLOCK"]'))
                 print "      |      |---N/A case number: %d " % len(suite.findall('set/testcase[@result="N/A"]'))
         except Exception, e:
            print "[ Error: When calculating the summary of Result XML, error: %s ]\n" % e

     def get_suites(self):
         suites = []
         if self.options.suites:
             for suite_str in self.options.suites:
                 suite_str_array = suite_str.split(" ")
                 for suite_name in suite_str_array:
                     suites.append(suite_name)
         return suites
     
     def check_sdb_devices(self):
         sdb_ok = False
         import subprocess

         proc = subprocess.Popen(["sdb devices"], stdout=subprocess.PIPE, shell=True)
         (out, err) = proc.communicate()
         print "sdb devices: %s" % out
         
         if self.options.deviceid is not None and self.options.deviceid[0] is not None:
             if self.options.deviceid[0] in out:
                 sdb_ok = True
                 print "The specified device %s is connected. Going to start testing" % self.options.deviceid[0]
             else:
                 print "The specified device %s is not connected. exiting" % self.options.deviceid[0]
         elif "device-1" in out:
             sdb_ok = True
             print "No device is specified, use the only connected USB device."
         else:
             print "No device is connected. exiting"

         return sdb_ok

