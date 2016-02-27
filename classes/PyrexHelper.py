class PyrexHelper:
    def __init__(self):
        pass

    def print_help(self):
        """
        print the helpf for pyrex
        """
        print("pyrex.py <parameters>")
        print("  -t <task>\t\tthe task PyRex should run")
        print("  -h <host>\t\tthe host where the task should run")
        print("  -g <group>\t\tthe host group where the task should run")
        print("  -a '<arguments>'\tadditional arguments for a task, enclosed in single quotes")
        print("\t\t\tformat: 'key1=value1,key2=value2'")
        print("  --hostlist\t\tprint a list of all defined hosts")
        print("  --configtest\t\tcheck the config.ini")
