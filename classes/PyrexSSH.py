from __future__ import print_function

import paramiko
import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


class PyrexSSH:
    def __init__(self, server):
        self.host = server['host']
        self.port = server['port']
        self.keyfile = server['keyfile']
        self.user = server['username']
        self.port = int(server['port'])
        self.servername = server['name']

    def run_cmd(self, cmd):
        logging.info("Running '%s' on %s" % (cmd, self.servername))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.user, key_filename=self.keyfile, port=self.port)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for line in stdout.readlines():
            print(line, end="")
        ssh.close()

    def upload_file(self, infile, outfile):
        print('Uploading file %s to %s' % (infile, self.servername + ':' + outfile))
        # get host key if we know one
        logging.info('Establishing SSH connection to: %s on port %s', self.host, self.port)
        t = paramiko.Transport((self.host, self.port))
        t.start_client()
        t.auth_publickey(self.user, paramiko.RSAKey.from_private_key_file(self.keyfile))
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(infile, outfile)
        t.close()
