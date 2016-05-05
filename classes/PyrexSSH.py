from __future__ import print_function

import paramiko
import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)


class PyrexSSH:
    """
    SSH functions for PyREX
    """
    def __init__(self, server):
        """
        class initialization
        """
        print('####################')
        self.servername = server['name']
        print('Name: ' + self.servername)
        self.host = server['host']
        print('Host: ' + self.host)
        self.port = int(server['port'])
        print('Port: ' + str(self.port))
        self.keyfile = server['keyfile']
        print('Key: ' + self.keyfile)
        self.user = server['username']
        print('User: ' + self.user)

    def run_cmd(self, cmd):
        """
        run a remote command
        """
        logging.info("Running '%s' on %s" % (cmd, self.servername))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.user, key_filename=self.keyfile, port=self.port)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for line in stdout.readlines():
            print(line, end="")
        ssh.close()

    def upload_file(self, infile, outfile):
        """
        upload a file via SSH
        """
        print('Uploading file %s to %s' % (infile, self.servername + ':' + outfile))
        logging.info('Establishing SSH connection to: %s on port %s', self.host, self.port)
        t = paramiko.Transport((self.host, self.port))
        t.start_client()
        t.auth_publickey(self.user, paramiko.RSAKey.from_private_key_file(self.keyfile))
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(infile, outfile)
        t.close()

    def download_file(self, source, target):
        """
        download a file via SSH
        """
        print('Downloading file %s to %s' % (self.servername + ':' + source, target))
        logging.info('Establishing SSH connection to: %s on port %s', self.host, self.port)
        t = paramiko.Transport((self.host, self.port))
        t.start_client()
        t.auth_publickey(self.user, paramiko.RSAKey.from_private_key_file(self.keyfile))
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(source, target)
        t.close()
