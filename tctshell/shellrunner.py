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

from xml.etree import ElementTree
import os
from constants import Constants
import glob
import datetime
import sys

class PlanSuite:
    def __init__(self, name, cmd):
        self.name = name
        self.cmd  = cmd
        os.chdir(Constants.TEST_SUITE_DIR)
        for files in glob.glob("*.rpm"):
            if files.startswith(name):
                self.file_name = files
                break
        if self.file_name is None:
            print "Error! the package %s is not found!" % name
    def get_name(self):
        return self.name

    def get_rpm_name(self):
        return self.file_name[0: -4]

    def get_command(self):
        return self.cmd

    def to_str(self):
        print "Suite: %s" % self.name
        print "Command: %s\n" % self.cmd 

    def install_suite(self, wrapper):
        print "Command: " + Constants.SDB_PUSH + " " + (Constants.RELEASED_SUITE_LOCATION % self.file_name) + " " + Constants.DEVICE_TMP_FOLDER + wrapper.get_sdb_device_id_param()
        os.system(Constants.SDB_PUSH + " " + (Constants.RELEASED_SUITE_LOCATION % self.file_name) + " " + Constants.DEVICE_TMP_FOLDER + wrapper.get_sdb_device_id_param())
        print "Command: " + Constants.SDB_SHELL + " " + (Constants.INSTALL_RPM % self.file_name) + wrapper.get_sdb_device_id_param()
        os.system(Constants.SDB_SHELL + " " + (Constants.INSTALL_RPM % self.file_name) + wrapper.get_sdb_device_id_param())

    def uninstall_suite(self, wrapper):
        print "Command: " + Constants.SDB_SHELL + " " +  (Constants.UNINSTALL_RPM % self.get_rpm_name())
        os.system(Constants.SDB_SHELL + " " +  (Constants.UNINSTALL_RPM % self.get_rpm_name()))

    def get_f(self):
        f = Constants.XMLFILE_PREFF + "\"" + Constants.DEVICE_TESTS_FILE % self.get_name()
        return Constants.add_right_enbrace(f)
    
    def get_e(self):
        e = Constants.EXECUTE_PREFF + "\"" + Constants.WRT_LAUNCHR_CMD + " %s" % self.get_name()
        return Constants.add_right_enbrace(e)

class PackageSuite:
    def __init__(self, name):
        self.name = name
        self.file_name = None
        os.chdir(Constants.TEST_SUITE_DIR)
        for files in glob.glob("*.rpm"):
            if files.startswith(name):
                self.file_name = files
                break
        if self.file_name is None:
            print "Error! the package %s is not found!" % name
        
    def get_name(self):
        return self.name

    def get_rpm_name(self):
        return self.file_name[0: -4]

    def to_str(self):
        print "Suite: %s" % self.name
        print "Package File: %s\n" % self.file_name

    def install_suite(self, wrapper):
        print "Command: " + Constants.SDB_PUSH + " " + (Constants.RELEASED_SUITE_LOCATION % self.file_name) + " " + Constants.DEVICE_TMP_FOLDER  + wrapper.get_sdb_device_id_param()
        os.system(Constants.SDB_PUSH + " " + (Constants.RELEASED_SUITE_LOCATION % self.file_name) + " " + Constants.DEVICE_TMP_FOLDER  + wrapper.get_sdb_device_id_param())
        print "Command: " + Constants.SDB_SHELL + " " + (Constants.INSTALL_RPM % self.file_name)  + wrapper.get_sdb_device_id_param()
        os.system(Constants.SDB_SHELL + " " + (Constants.INSTALL_RPM % self.file_name)  + wrapper.get_sdb_device_id_param())

    def uninstall_suite(self, wrapper):
        print "Command: " + Constants.SDB_SHELL + " " +  (Constants.UNINSTALL_RPM % self.get_rpm_name()) + wrapper.get_sdb_device_id_param()
        os.system(Constants.SDB_SHELL + " " +  (Constants.UNINSTALL_RPM % self.get_rpm_name()) + wrapper.get_sdb_device_id_param())

    def get_f(self):
        f = Constants.XMLFILE_PREFF + "\"" + Constants.DEVICE_TESTS_FILE % self.get_name()
        return Constants.add_right_enbrace(f)
    
    def get_e(self):
        e = Constants.EXECUTE_PREFF + "\"" + Constants.WRT_LAUNCHR_CMD + " %s" % self.get_name()
        return Constants.add_right_enbrace(e)

class RerunFailSuite:
     def __init__(self, suite):
         self.name = suite.get("name")
         self.file_name = None
         os.chdir(Constants.TEST_SUITE_DIR)
         for files in glob.glob("*.rpm"):
             if files.startswith(self.name):
                 self.file_name = files
                 break
         if self.file_name is None:
             print "Error! the package %s is not found!" % name

         self.suite = suite
         print "parsing the suite: " + self.name
         i = 0
         if (self.suite is not None) and (self.suite.findall('set/testcase') is not None):
             print "Case number: " + str(len(self.suite.findall('set/testcase')))
             for testset in self.suite.findall("set"):
                 for testcase in testset.findall('testcase'):
                     i = i+1
                     result = testcase.get("result")
                     if (result is not None) and (cmp(result, "PASS") == 0):
                         #print "Removing testcase: " + testcase.get("purpose")
                         testset.remove(testcase)
                     else:
                         testcase.remove(testcase.find('result_info'))
                         testcase.set('result', "")
             print "Unpassed Case number: " + str(len(self.suite.findall('set/testcase')))

     def is_empty(self):
         return (self.suite.findall('set/testcase') is None)

     def to_str(self):
         print "Suite: %s" % self.name
         print "Package File: %s\n" % self.file_name

     def to_xml(self):
         xml_name = self.name + ".xml"
         print "generating XML "+ xml_name
         root = ElementTree.Element('test_definition')
         root.append(self.suite)
         tree = ElementTree.ElementTree()
         tree._setroot(root)
         tree.write(xml_name, encoding="utf-8")

     def get_rerunxml_name(self):
         folder_name = Constants.TEMP_UNPASSED_XML_FOLDER
         if not folder_name.endswith('/'):
             folder_name = folder_name + "/"
         return folder_name + self.name + ".xml"         
     
     def get_name(self):
         return self.name

     def get_rpm_name(self):
         return self.file_name[0: -4]

     def install_suite(self, wrapper):
         print "Command: " + Constants.SDB_PUSH + " " + (Constants.RELEASED_SUITE_LOCATION % self.file_name) + " " + Constants.DEVICE_TMP_FOLDER + wrapper.get_sdb_device_id_param()
         os.system(Constants.SDB_PUSH + " " + (Constants.RELEASED_SUITE_LOCATION % self.file_name) + " " + Constants.DEVICE_TMP_FOLDER  + wrapper.get_sdb_device_id_param())
         print "Command: " + Constants.SDB_SHELL + " " + (Constants.INSTALL_RPM % self.file_name) + wrapper.get_sdb_device_id_param()
         os.system(Constants.SDB_SHELL + " " + (Constants.INSTALL_RPM % self.file_name) + wrapper.get_sdb_device_id_param())

     def uninstall_suite(self, wrapper):
         print "Command: " + Constants.SDB_SHELL + " " +  (Constants.UNINSTALL_RPM % self.get_rpm_name()) + wrapper.get_sdb_device_id_param()
         os.system(Constants.SDB_SHELL + " " +  (Constants.UNINSTALL_RPM % self.get_rpm_name()) + wrapper.get_sdb_device_id_param())

     def get_f(self):
        f = "-f \"" + Constants.TEMP_UNPASSED_XML_FOLDER + self.name + ".xml"
        return Constants.add_right_enbrace(f)
    
     def get_e(self):
        e = Constants.EXECUTE_PREFF + "\"" + Constants.WRT_LAUNCHR_CMD + " %s" % self.get_name()
        return Constants.add_right_enbrace(e)

class TotalSummary:
    def __init__(self, plan_name):
        self.plan_name           = plan_name
        self.suite_summary_array = []
        self.environment_elm     = None
        self.summary_elm         = None
        self.capabilities        = None

    def set_summary(self, summary):
        self.summary_elm = summary

    def set_environment(self, environment):
        self.environment_elm = environment

    def add_suite_elm(self, suite_elm):
        self.suite_summary_array.append(SuiteSummary(suite_elm))

    def set_capabilities(self, capabilities):
        self.capabilities = capabilities
    
    def to_xml(self):
        result_summary = ElementTree.Element('result_summary')
        result_summary.set('plan_name', self.plan_name)
        if self.environment_elm is not None:
            ElementTree.dump(self.environment_elm)
            result_summary.append(self.environment_elm)
        if self.summary_elm is not None:
            ElementTree.dump(self.summary_elm)
            result_summary.append(self.summary_elm)
        if self.capabilities is not None:
            ElementTree.dump(self.capabilities)
            result_summary.append(self.capabilities)
        for suite in self.suite_summary_array:
            result_summary.append(suite.to_xml())
        return result_summary

class SuiteSummary:
    def __init__(self, xml_suite):
        self.name = xml_suite.get('name')
        self.tc_total   = len(xml_suite.findall('set/testcase'))
        self.tc_pass    = len(xml_suite.findall('set/testcase[@result="PASS"]'))
        self.tc_fail    = len(xml_suite.findall('set/testcase[@result="FAIL"]'))
        self.tc_block   = len(xml_suite.findall('set/testcase[@result="BLOCK"]'))
        self.tc_na      = len(xml_suite.findall('set/testcase[@result="N/A"]'))
        if self.tc_total > 0:
            self.pass_rate  = self.tc_pass * 100 / self.tc_total
            self.fail_rate  = self.tc_fail * 100 / self.tc_total
            self.block_rate = self.tc_block * 100 / self.tc_total
            self.na_rate    = self.tc_na * 100 / self.tc_total
        else:
            self.pass_rate  = 0
            self.fail_rate  = 0
            self.block_rate = 0
            self.na_rate    = 0

    def to_str(self):
        print " Suite: %s" % self.name
        print "      |---total case number: %d " % self.tc_total 
        print "      |      |---Pass rate: %d" % self.pass_rate
        print "      |      |---PASS case number: %d " % self.tc_pass
        print "      |      |---FAIL rate: %d" % self.fail_rate
        print "      |      |---FAIL case number: %d " % self.tc_fail
        print "      |      |---BLOCK rate: %d" % self.block_rate
        print "      |      |---BLOCK case number: %d " % self.tc_block
        print "      |      |---N/A rate: %d" % self.na_rate
        print "      |      |---N/A case number: %d " % self.tc_na

    def to_xml(self):
        suite_elm = ElementTree.Element('suite')
        suite_elm.set('name', self.name)

        total_case      = ElementTree.SubElement(suite_elm, 'total_case')
        total_case.text = str(self.tc_total)

        pass_case      = ElementTree.SubElement(suite_elm, 'pass_case')
        pass_case.text = str(self.tc_pass)
        pass_rate      = ElementTree.SubElement(suite_elm, 'pass_rate')
        pass_rate.text = str(self.pass_rate)

        fail_case      = ElementTree.SubElement(suite_elm, 'fail_case')
        fail_case.text = str(self.tc_fail)
        fail_rate      = ElementTree.SubElement(suite_elm, 'fail_rate')
        fail_rate.text = str(self.fail_rate)

        block_case      = ElementTree.SubElement(suite_elm, 'block_case')
        block_case.text = str(self.tc_block)
        block_rate      = ElementTree.SubElement(suite_elm, 'block_rate')
        block_rate.text = str(self.block_rate)

        na_case      = ElementTree.SubElement(suite_elm, 'na_case')
        na_case.text = str(self.tc_na)
        na_rate      = ElementTree.SubElement(suite_elm, 'na_rate')
        na_rate.text = str(self.na_rate)
        
        return suite_elm

class WrapperRunner:

    def __init__(self):
        self.suites = {}
        self.running_mode = None
        self.latest_result_folder = Constants.TEMP_RESULT_XML_FOLDER + "%s/" % datetime.datetime.now()
        self.summary = None

    def create_result_folder(self):
        d = os.path.dirname(Constants.TEMP_RESULT_XML_FOLDER)
        if not os.path.exists(d):
            os.makedirs(d)
        os.chdir(Constants.TEMP_RESULT_XML_FOLDER)
        os.system("rm latest")
        d = os.path.dirname(self.latest_result_folder) 
        os.makedirs(d)
        link = "ln -s '%s' '%s'" % (self.latest_result_folder, "latest")
        os.system(link)

    def check_capability_suite(self):
        is_include = False
        for suite_name in self.suites:
            if Constants.CAPABILITY_SUITE_NAME in suite_name:
                is_include = True
                break
        return is_include

    def exit_without_capability(self, wrapper):
        print "Checking capability"
        if not wrapper.is_cap_param_available():
            if self.check_capability_suite():
                print "The capability related suite is in the plan, but no capability XML is available. Please refer to the file %scapability.xml to edit and input capability XML file before running test" % Constants.TCT_PLAN_FOLDER
                sys.exit(1)

    def execute_suite_in_loop(self, wrapper):
        self.create_result_folder()
        if wrapper.is_fail_rerun_mode():
            self.rebuild_fail_xml()
        for suite_name in self.suites:
            suite = self.suites[suite_name]
            if wrapper.is_auto_install():
                print "installing suite: %s" % suite_name
                suite.install_suite(wrapper)
            f = suite.get_f()
            e = suite.get_e()
            command = "testkit-lite %s " % (f + " " + e)
            command += "%s " % wrapper.get_memory_param()
            command += "%s " % wrapper.get_skip_native_manual_cases_param()
            command += "%s " % wrapper.get_deviceid_param()
            command += "%s " % wrapper.get_capability_param()
            command += "%s " % wrapper.get_auto_case_param()
            command += "%s " % wrapper.get_manual_case_param()
            command += "%s " % wrapper.get_testcase_id()
            command += " -o \"%s.xml\"" % (self.latest_result_folder + suite_name)
            if wrapper.is_fail_rerun_mode():
                command += " --rerun"
            print command
            os.system(command)

            if wrapper.is_auto_install():
                print "uninstalling suite: %s" % suite_name
                suite.uninstall_suite(wrapper)

    def select_start_at(self, start_at, this_start_at):
        if start_at is None:
            return this_start_at
        elif cmp(start_at, this_start_at) < 0:
            return start_at
        else:
            return this_start_at

    def select_end_at(self, end_at, this_end_at):
        if end_at is None:
            return this_end_at
        elif cmp(end_at, this_end_at) > 0:
            return end_at
        else:
            return this_end_at

    def copy_result_xml(self, result_xml):
        print "Copying the merged result XML '%s'" % result_xml + "to %s" % self.latest_result_folder        
        os.system("cp " + result_xml + " '" + self.latest_result_folder + "'")

    def merge_suite_result(self, result_xml, plan_name):
        os.chdir(self.latest_result_folder)
        root        = ElementTree.Element('test_definition')
        first       = True
        start_at    = None 
        end_at      = None
        summary_xml = TotalSummary(plan_name)

        for suite_name in self.suites:
            result_name = "%s.xml" % suite_name
            if os.path.isfile(result_name):
                print "Reading the result of suite : %s" % suite_name
                if True:
                    xml_tree = ElementTree.parse(result_name)
                    xml_root = xml_tree.getroot()
                    if first:
                        first = False
                        env_elm = xml_root.find('environment')
                        root.append(env_elm)
                        summary_xml.set_environment(env_elm)
                        root.append(xml_root.find('summary'))
                    summary    = xml_root.find('summary')
                    this_start = summary.find('start_at')
                    this_end   = summary.find('end_at')

                    start_at = self.select_start_at(start_at, this_start.text)
                    end_at   = self.select_end_at(end_at, this_end.text)
                        
                    for this_suite in xml_root.findall('suite'):
                        root.append(this_suite)
                        summary_xml.add_suite_elm(this_suite)
            else:
                print "[Error] the expecting result of the suite %s is not found! " % suite_name
        s_tag = root.find('summary/start_at')
        if s_tag is not None: 
            s_tag.text = start_at
        e_tag = root.find('summary/end_at')
        if e_tag is not None:
            e_tag.text = end_at

        sum_elm = root.find('summary')
        summary_xml.set_summary(sum_elm)

        capability_root = self.parse_capablities()
        summary_xml.set_capabilities(capability_root)

        tree = ElementTree.ElementTree()
        tree._setroot(root)

        d = os.path.abspath(os.path.dirname(result_xml))

        if not os.path.exists(d):
            os.makedirs(d)
 
        tree.write(result_xml, encoding="utf-8")
        print "Generating the merged result XML '%s'" % result_xml

        sum_tree = ElementTree.ElementTree()
        sum_root = summary_xml.to_xml()
        Constants.indent(sum_root)
        sum_tree._setroot(sum_root)
        print "Generating the summary XML in %s" % (self.latest_result_folder + "summary.xml")
        outFile = open(self.latest_result_folder + "summary.xml", 'w')
        outFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        outFile.write("<?xml-stylesheet type=\"text/xsl\" href=\"summary.xsl\"?>\n")

        sum_tree.write(outFile, encoding="utf-8")
        outFile.close()

    def pull_device_capabilities(self, wrapper):
        rm_command = 'rm ' + Constants.CAPABILITY_PATH
        print "Command: " + rm_command
        os.system(rm_command)
        
        pull_command = Constants.SDB_PULL % wrapper.get_sdb_device_id_param() + " " + Constants.DEVICE_CAPABILITY_PATH + " " + Constants.CAPABILITY_PATH
        print "Command: " + pull_command
        os.system(pull_command) 

    def parse_capablities(self):
        root = ElementTree.Element('capabilities')
        try:
            capa_root = None
            capa_tree = ElementTree.parse(Constants.CAPABILITY_PATH)
            capa_root = capa_tree.getroot()

            for capa in capa_root.findall('capability'):
                root.append(capa)
        except Exception, e:
            print "[ Error: reading capability XML fail, error: %s ]\n" % e
            root = None
        return root 

    def open_report(self):
        Constants.copy_style_in_result_folder(self.latest_result_folder)

    def prepare_testplan(self, testplan_xml, running_mode, f_suites, result_xml):
        print "preparing test plan"
        self.running_mode = running_mode
        if running_mode == Constants.RUNNING_MODE_PLAN:
            self.load_testplan_xml(testplan_xml)
        elif running_mode == Constants.RUNNING_MODE_RESULT:
            print "reading result..."
            self.read_result_xml(result_xml)
        elif running_mode == Constants.RUNNING_MODE_SUITES:
            self.prepare_pkg(f_suites)
        elif running_mode == None:
            os.system("tct-shell -h")
            print "\ntct-shell: Command requires a running mode"
            sys.exit(1)

    def load_testplan_xml(self, testplan_xml):
        try:
            xml_tree = ElementTree.parse(testplan_xml)
            xml_root = xml_tree.getroot()
            # all suites
            for xml_suite in xml_root.findall('suite'):
                suite = PlanSuite(xml_suite.get("name"), xml_suite.find("command").text)
                self.suites[suite.get_name()] = suite
                suite.to_str()
        except Exception, e:
            print "[ Error: reading testplan XML fail, error: %s ]\n" % e
            sys.exit(1)

    def prepare_pkg(self, f_suites):
        if f_suites:
            for suite_name in f_suites:
                suite = PackageSuite(suite_name)
                self.suites[suite.get_name()] = suite
                suite.to_str()

    def generate_params(self):
        f = Constants.XMLFILE_PREFF + "\""
        tmp = ""
        for suite in self.suites.keys():
            suite_obj = self.suites[suite]
            p_name = suite[0: suite.find("tests")] + "tests"
            f += Constants.DEVICE_TESTS_FILE % p_name
            if suite_obj.get_command().startswith(Constants.WRT_LAUNCHR_CMD):
                tmp += "%s " % suite_obj.get_command()[(len(Constants.WRT_LAUNCHR_CMD) + 1):]
        f = Constants.add_right_enbrace(f)
        e = ""
        if not tmp.isspace():
            e = Constants.EXECUTE_PREFF  + "\"" + Constants.WRT_LAUNCHR_CMD +" " + tmp
            e = Constants.add_right_enbrace(e)
        return f + " " + e

    def generate_rerun_params(self):
        f = "-f \""
        param = Constants.EXECUTE_PREFF  + "\"" + Constants.WRT_LAUNCHR_CMD
        for suite in self.suites.keys():
            suite_obj = self.suites[suite]
            f += "%s " % suite_obj.get_rerunxml_name()
            param += " %s" % suite
        f = Constants.add_right_enbrace(f)
        param = Constants.add_right_enbrace(param)
        return f + param + Constants.RERUN_OUTPUT

    def read_result_xml(self, result_xml):
        try:
            xml_tree = ElementTree.parse(result_xml)
            xml_root = xml_tree.getroot()
            # all suites
            for xml_suite in xml_root.findall('suite'):
                suite = RerunFailSuite(xml_suite)
                if suite.is_empty():
                    print "No unpassed test cases is found in the suite %s; skip it!" % suite.get_name()
                else:
                    self.suites[suite.get_name()] = suite
        except Exception, e:
            print "[ Error: reading original Result XML fail, error: %s ]\n" % e
            sys.exit(1)

    def rebuild_fail_xml(self):
        folder_name = Constants.TEMP_UNPASSED_XML_FOLDER
        if not folder_name.endswith('/'):
            folder_name = folder_name + "/"
        d = os.path.dirname(Constants.TEMP_UNPASSED_XML_FOLDER)
        if not os.path.exists(d):
            print "Creating"
            os.makedirs(d)
        os.chdir(Constants.TEMP_UNPASSED_XML_FOLDER)

        for suite_name in self.suites.keys():
            suite = self.suites[suite_name]
            suite.to_xml()

    def merge_result_xml(self, origin_xml, result_xml):
        try:
            origin_tree = ElementTree.parse(origin_xml)
            origin_root = origin_tree.getroot()
            
            new_tree = ElementTree.parse(result_xml)
            new_root = new_tree.getroot()

            for new_tc in new_root.findall('suite/set/testcase'):
                condition = './testcase[@purpose="%s"]' % new_tc.get("purpose")
                for origin_set in origin_root.findall('suite/set'):
                    target = origin_set.find(condition)
                    if target is not None:
                        origin_set.remove(target)
                        origin_set.append(new_tc)
                        break
            origin_tree.write(origin_xml, encoding="utf-8")
        except Exception, e:
            print "[ Error: reading suite Result XML fail, error: %s ]\n" % e


