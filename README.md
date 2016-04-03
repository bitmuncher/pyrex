Remote Execution with Python<br />
<br />
PyREX is a remote execution system written in Python. It runs commands via SSH<br />
on one or multiple hosts. <br />
<br />
Usage:<br />
<br />
pyrex.py <parameters><br />
  -t <task>		the task PyRex should run<br />
  -h <host>		the host where the task should run<br />
  -g <group>	    	the host group where the task should run<br />
  -a '<arguments>'	additional arguments for a task, enclosed in single quotes<br />
     			format: 'key1=value1,key2=value2'<br />
  --hostlist		print a list of all defined hosts<br />
  --configtest		check the config.ini<br />
<br />
You can run multiple commands at once if you use task files<br />
(for an example see tasks/test.task). Task names are the file names without the<br />
.task extension. For example: If you have a task file with name 'foobar.task' the<br />
task name is 'foobar'.<br />
<br />
There is a special case for task 'runcmd'. This task runs without a template and<br />
executes the command given with '-a'. <br />
<br />
You can specify hosts and hostgroups in config.ini.<br />
<br />
Syntax of config.ini:<br />
<br />
<pre>
---- SNIP ----
[Config]
# this is the section for main configurations of PyREX

[HostGroups]
# you can specify the hostgroups here
hostgroup1: host1, host2

# all hosts need a section
[host1]
# domain or IP
Host: foobar.host.tld
# name is equal to section name
Name: host1
# the SSH port
Port: 22
# the ssh key file, PyREX don't support passwords
Keyfile: /path/to/keyfile/for/ssh
# SSH user
Username: yoursshuser
# sudo flag - 1 = use sudo, 0 = don't use sudo
Sudo: 1 
---- SNIP ----
</pre>
