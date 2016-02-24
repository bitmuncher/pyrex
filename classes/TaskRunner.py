import sys
import os.path
import re

import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

from classes.PyrexHelper import PyrexHelper
phelper = PyrexHelper()

from classes.PyrexSSH import PyrexSSH
pssh = PyrexSSH()

import classes.PyrexConfig as pcfg
#import ConfigParser as cfgp


class TaskRunner:
    def __init__(self):
        pass

    def check_task(self, task, config):
        """
        check if a task template is available
        """
        config_section = pcfg.ConfigSectionMap(config, 'Config')
        taskdir = config_section['taskdir']
        taskfile = taskdir + '/' + task + '.task'
        if os.path.isfile(taskfile):
            return True
        else:
            return False

    def parse_task(self, host, task, args, config):
        # get the task file content
        config_section = pcfg.ConfigSectionMap(config, 'Config')
        taskdir = config_section['taskdir']
        taskfile = taskdir + '/' + task + '.task'
        f = open(taskfile, 'r')
        args_parts = args.split(',')
        arg_list = {}
        for arg in args_parts:
            arg_parts = arg.split('=')
            arg_list[arg_parts[0]] = arg_parts[1]
        for line in iter(f):
            logging.debug(line)
            lineparts = line.split()
            if lineparts[0] == '#':
                # found a comment, go to next line
                logging.debug("Comment... going to next line")
                continue
            elif lineparts[0] == 'upload':
                fromfile = ''
                tofile = ''
                # replace inline tags in filenames
                if lineparts[1].find('{') and lineparts[1].find('}'):
                    # we have a tag, replace it with the value from args
                    for k in arg_list:
                        if lineparts[1].find('{' + arg_list[k] + '}'):
                            fromfile = lineparts[1].replace('{' + k + '}', arg_list[k])
                else:
                    fromfile = lineparts[1]
                if lineparts[2].find('{') and lineparts[2].find('}'):
                    # we have a tag, replace ist with the value from args
                    for k in arg_list:
                        if lineparts[2].find('{' + arg_list[k] + '}'):
                            tofile = lineparts[2].replace('{' + k + '}', arg_list[k])
                else:
                    tofile = lineparts[2]
                logging.debug('Uploading file ' + fromfile + ' to target ' + tofile)

        f.close()
        return True

    def run_task_host(self, host, task, args, config):
        """
        run a task on a specific host
        """
        # check if task exists
        if not self.check_task(task, config):
            print "Couldn't find a template for the specified task"
            sys.exit(0)
        # get the commands we have to run
        retval = self.parse_task(host, task, args, config)
        if retval is False:
            print "Something is wrong with the task defintion!"
            sys.exit(0)

    def run_task(self, config, task=None, host=None, hostgroup=None, args=None):
        """
        entry point for the task runner
        """
        # check parameters
        if task is None:
            print("Please specify a task to run.")
            phelper.print_help()
            sys.exit(1)
        if host is None and hostgroup is None:
            print("You must specify a group or a host for the task.")
            phelper.print_help()
            sys.exit(1)
        if host is not None and hostgroup is not None:
            print("Please specify either a host or a hostgroup.")
            phelper.print_help()
            sys.exit(1)

        # we have a special case for task 'runcmd'
        # no task template is needed for it
        if task == 'runcmd':
            if args is None:
                print "Please specify a command to run with \"--args='yourcommand'\""
                phelper.print_help()
                sys.exit(1)
            logging.debug("Calling run_cmd() with host=%s, hostgroup=%s cmd=%s" % (host, hostgroup, args))
            self.run_cmd(config, cmd=args, host=host, hostgroup=hostgroup)
            sys.exit(0)
        else:
            if hostgroup is None and host is not None:
                # we have a given host, run the task directly
                self.run_task_host(host, task, args, config)
            elif hostgroup is not None and host is None:
                hosts = pcfg.get_hosts_by_hostgroup(config, hostgroup)
                for host in hosts:
                    self.run_task_host(host, task, args, config)

    def run_cmd(self, config, cmd=None, host=None, hostgroup=None):
        """
        run a command on a specific host or hostgroup
        """
        if hostgroup is None:
            # run on a specific host
            # first get the needed data from the config
            server_data = pcfg.ConfigSectionMap(config, host)
            # and now run the command on the host
            pssh.run_cmd(server_data, cmd)
        else:
            # we have a hostgroup
            # first get all hosts for this hostgroup
            hostgroups = pcfg.ConfigSectionMap(config, 'HostGroups')
            try:
                hostgroup_hostlist = hostgroups[hostgroup]
            except:
                print("Unknown hostgroup.\nUse '--hostlist' to see all available hostgroups and their hosts.")
                sys.exit(1)
            hostlist = hostgroup_hostlist.split(',')
            for host in hostlist:
                server_data = pcfg.ConfigSectionMap(config, host)
                # run the command
                pssh.run_cmd(server_data, cmd)
