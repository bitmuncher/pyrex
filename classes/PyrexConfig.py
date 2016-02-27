def ConfigSectionMap(config, section):
    """
    return a dictionary with all settings from the specified section
    """
    config_dict = {}
    options = config.options(section)
    for option in options:
        try:
            config_dict[option] = config.get(section, option)
        except:
            print("exception on %s" % option)
            config_dict[option] = None
    return config_dict


def get_hosts_by_hostgroup(config, hostgroup):
    """
    get a list of all hosts from a hostgroup definition in config
    """
    hostgroups = ConfigSectionMap(config, 'HostGroups')
    hostlist = hostgroups[hostgroup].split(',')
    return hostlist
