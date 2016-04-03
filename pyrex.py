#!/usr/bin/python2

# we use the python 3 print function here
from __future__ import print_function

import sys
import getopt

from classes.PyrexHelper import PyrexHelper
phelper = PyrexHelper()

from classes.TaskRunner import TaskRunner
trunner = TaskRunner()

import classes.PyrexConfig as pcfg

import ConfigParser as cfgp

import logging
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)


def print_all_hosts(config):
    """
    print a list of all hosts which are defined in config.ini
    """
    print("Available hostgroups and hosts:")
    # get the hostgroups
    hostgroups = config.options('HostGroups')
    for hostgroup in hostgroups:
        print("[%s]" % hostgroup)
        hostlist = config.get('HostGroups', hostgroup)
        hosts = hostlist.split(',')
        for host in hosts:
            host_name = host
            host_host = config.get(host_name, 'Host')
            print("%s => %s" % (host_name, host_host))


def validate_config(config):

    """
    function to check the config.ini for PyRex
    """
    # check if we have hostgroups and host definitions
    # for all hosts in this groups
    hostgroups = pcfg.ConfigSectionMap(config, 'HostGroups')
    config_error = 0
    for hostgroup in hostgroups:
        print('\nChecking group [%s]' % hostgroup)
        hostlist = hostgroups[hostgroup].split(',')
        for host in hostlist:
            print('\n')
            print('Checking host %s' % host)
            hostdata = pcfg.ConfigSectionMap(config, host)
            # we expect the following data
            host_host = None
            host_port = None
            host_keyfile = None
            host_username = None
            host_sudo = None
            # ok... let's try
            try:
                host_host = hostdata['host']
                print("Host for %s found: %s" % (host, host_host))
            except:
                print('Missing host definition for %s\nPlease add \'Host\' for this host.' % (host))
                config_error = 1
            try:
                host_port = int(hostdata['port'])
                print("Port for %s found: %s" % (host, host_port))
            except:
                print('Missing or invalid port definition for %s\nPlease check the \'Port\' parameter for this host.' % (host))
                config_error = 1
            try:
                host_keyfile = hostdata['keyfile']
                print("Keyfile for %s found: %s" % (host, host_keyfile))
            except:
                print('Missing key file definition for %s\n')
                print('Please add \'Keyfile\' for this host.' % host)
                config_error = 1
            try:
                host_username = hostdata['username']
                print("Username for %s found: %s" % (host, host_username))
            except:
                print('Missing user name definition for %s\n')
                print('Please add \'Username\' for this host.' % host)
                config_error = 1
            try:
                host_sudo = int(hostdata['sudo'])
                print('Sudo flag for %s found: %s' % (host, host_sudo))
            except:
                print('Missing or invalid sudo definition for %s\n')
                print('Please check if \'Sudo\' is defined for this host and is set to 1 or 0')
                config_error = 1
    if config_error == 1:
        print("Errors in your config.ini found.\n")
        print("Please check the output from this config test for more details.")
        sys.exit(1)
    print("\nYour configuration seems to be fine.")
    sys.exit(0)


def main(argv):
    """
    Main function for PyRex
    """
    task = None
    host = None
    hostgroup = None
    add_args = None

    # read configuration
    config = cfgp.ConfigParser()
    config.read('config.ini')

    try:
        opts, args = getopt.getopt(argv, "t:g:h:a:",
            ["task=",
             "group=",
             "hostgroup=",
             "host=",
             "hostlist",
             "configtest",
             "args="])
    except:
        logging.debug("Exception")
        phelper.print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-t', '--task'):
            logging.info('Task: %s' % arg)
            task = arg
        elif opt in ('-h', '--host'):
            logging.info('Host: %s' % arg)
            host = arg
        elif opt in ('-g', '--group', '--hostgroup'):
            logging.info('Hostgroup: %s' % arg)
            hostgroup = arg
        elif opt == '--hostlist':
            print_all_hosts(config)
            sys.exit(0)
        elif opt == '--configtest':
            validate_config(config)
            sys.exit(0)
        elif opt in ('-a', '--args'):
            logging.info("Additional args: %s" % arg)
            add_args = arg

    # run the task with TaskRunner
    logging.debug("Calling task runner with task=%s, host=%s, hostgroup=%s, add_args='%s'" % (task, host, hostgroup, add_args))
    trunner.run_task(config, task, host, hostgroup, add_args)

if __name__ == '__main__':
    main(sys.argv[1:])
