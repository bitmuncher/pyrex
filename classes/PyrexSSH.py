from __future__ import print_function

import paramiko


class PyrexSSH:
    def __init__(self):
        pass

    def run_cmd(self, server, cmd):
        print(server)
        host = server['host']
        port = server['port']
        keyfile = server['keyfile']
        user = server['username']
        port = int(server['port'])
        servername = server['name']

        print('\n' + servername + '\n')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, key_filename=keyfile, port=port)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for line in stdout.readlines():
            print(line, end="")
        ssh.close()
