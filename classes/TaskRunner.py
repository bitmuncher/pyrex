import sys
import os.path
import os

import logging
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

from classes.PyrexHelper import PyrexHelper
phelper = PyrexHelper()

from classes.PyrexSSH import PyrexSSH

import classes.PyrexConfig as pcfg
#import ConfigParser as cfgp


class TaskRunner:
    """
    This class executes a task.
    Execution order:
        run_task()
            run_cmd() if task name is 'runcmd'
        check_task()
        run_task_host()
        parse_task()
            replace_tag()
    """

    def __init__(self):
        # nothing to do here
        pass

    def check_task(self, task, config):
        """
        check if a task template is available
        """
        # get the task file path
        config_section = pcfg.ConfigSectionMap(config, 'Config')
        taskdir = config_section['taskdir']
        taskfile = taskdir + '/' + task + '.task'
        # check if the task exists
        if os.path.isfile(taskfile):
            return True
        else:
            return False

    def replace_tag(self, linepart, arg_list):
        """
        replace tags in a string by given arguments
        """
        if linepart.find('{') and linepart.find('}'):
            # we have a tag, replace it
            for k in arg_list:
                if linepart.find('{' + k + '}'):
                    linepart = linepart.replace('{' + k + '}', arg_list[k])
        # if we still have a tag, ask for the value
        if linepart.find('{') and linepart.find('}'):
            # extract the tag name
            start = linepart.find('{')
            end = linepart.find('}')
            if start != -1 and end != -1:
                # ask for the value for this tag
                print 'No argument for tag \'' + linepart[start + 1:end] + '\'!'
                val = raw_input('Please enter a value for \'' + linepart[start + 1:end] + '\': ')
                # add the value to arg_list
                arg_list[linepart[start + 1:end]] = val
                # replace the tag in the current line
                linepart = linepart.replace('{' + linepart[start + 1:end] + '}', val)
        return linepart

    def run_task_host(self, host, task, args, config):
        """
        run a task on a specific host
        """
        print '\n' + host + '\n'
        # check if task exists
        if not self.check_task(task, config):
            logging.error("Couldn't find a template for the specified task")
            sys.exit(0)
        # get the commands we have to run
        retval = self.parse_task(host, task, args, config)
        if retval is False:
            print "Something is wrong with the task defintion!"
            sys.exit(0)

    def parse_task(self, host, task, args, config):
        """
        parse a task file
        """
        # get the task file path
        config_section = pcfg.ConfigSectionMap(config, 'Config')
        server_data = pcfg.ConfigSectionMap(config, host)
        taskdir = config_section['taskdir']
        taskfile = taskdir + '/' + task + '.task'

        # open task file
        f = open(taskfile, 'r')

        # get the list of -a parameters
        arg_list = {'tag': 'replacement'}
        if args and args is not '':
            args_parts = args.split(',')
            for arg in args_parts:
                arg_parts = arg.split('=')
                arg_list[arg_parts[0]] = arg_parts[1]

        for line in iter(f):
            logging.debug('...')
            # skip empty lines
            if line == '\n':
                logging.debug('Empty line... going to next line')
                continue

            logging.debug('Line: ' + line.rstrip())
            lineparts = line.split()

            # # - comments
            if lineparts[0] == '#':
                logging.debug("Comment... going to next line")
                continue

            # upload - file uploads
            elif lineparts[0] == 'upload':
                fromfile = self.replace_tag(lineparts[1], arg_list)
                tofile = self.replace_tag(lineparts[2], arg_list)
                logging.debug('Uploading file ' + fromfile + ' to target ' + tofile)
                pssh = PyrexSSH(server_data)
                pssh.upload_file(fromfile, tofile)

            # download - file downloads
            elif lineparts[0] == 'download':
                source = self.replace_tag(lineparts[1], arg_list)
                target = self.replace_tag(lineparts[2], arg_list)
                logging.debug('Downloading file ' + source + ' to target ' + target)
                pssh = PyrexSSH(server_data)
                pssh.download_file(source, target)

            # remoterun - run a command on the remote host
            elif lineparts[0] == 'remoterun':
                # run a command on the specified host
                cmd_str = ''
                i = 0
                for cmd_part in lineparts[1:]:
                    cmd_part = self.replace_tag(cmd_part, arg_list)
                    if i > 0:
                        cmd_str += ' ' + cmd_part
                    else:
                        cmd_str += cmd_part
                    i += 1
                logging.debug('Running command on host: ' + cmd_str)
                pssh = PyrexSSH(server_data)
                pssh.run_cmd(cmd_str)

            # localrun - run a command on localhost
            elif lineparts[0] == 'localrun':
                cmd_str = ''
                i = 0
                for cmd_part in lineparts[1:]:
                    cmd_part = self.replace_tag(cmd_part, arg_list)
                    if i > 0:
                        cmd_str += ' ' + cmd_part
                    else:
                        cmd_str += cmd_part
                    i += 1
                logging.debug('Running local command: ' + cmd_str)
                os.system(cmd_str)

        f.close()
        return True

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
            else:
                logging.error('Please specify either a host or a hostgroup')

    def run_cmd(self, config, cmd=None, host=None, hostgroup=None):
        """
        run a command on a specific host or hostgroup
        """
        if hostgroup is None:
            # run on a specific host
            # first get the needed data from the config
            server_data = pcfg.ConfigSectionMap(config, host)
            # and now run the command on the host
            pssh = PyrexSSH(server_data)
            pssh.run_cmd(cmd)
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
                pssh = PyrexSSH(server_data)
                pssh.run_cmd(cmd)
