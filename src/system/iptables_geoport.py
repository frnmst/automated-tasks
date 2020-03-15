#!/usr/bin/env python3
#
# iptables_geoport.py
#
# Copyright (C) 2020  Franco Masotti <franco.masotti@live.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# OLD NOTICES
## See url for more info - http://www.cyberciti.biz/faq/?p=3402
## Author: nixCraft <www.cyberciti.biz> under GPL v.2.0+
## Post Author: frnmst (Franco Masotti) franco.masotti@live.com
## New version heavily based on https://wiki.archlinux.org/index.php/Simple_stateful_firewall
##   https://wiki.archlinux.org/index.php/Iptables
##   and a little on http://www.thegeekstuff.com/2011/06/iptables-rules-examples/ as well as nixCraft for the bash stuff.


import copy
import requests
import sys
import shlex
import ipaddress
import subprocess
import urllib
import pathlib
import os
import yaml


class UserNotRoot(Exception):
    r"""The user running the script is not root."""

##################
# Basic commands #
##################

def reset_rules():
    r"""Reset the chains and the tables."""
    # https://wiki.archlinux.org/index.php/Iptables#Resetting_rules
    #
    # Copyright (C) 2020 Arch Wiki contributors.
    # Permission is granted to copy, distribute and/or modify this document
    # under the terms of the GNU Free Documentation License, Version 1.3
    # or any later version published by the Free Software Foundation;
    # with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    # A copy of the license is included in the section entitled "GNU
    # Free Documentation License".
    commands = dict()
    commands['flush'] = 'iptables --flush'
    commands['delete chain'] = 'iptables --delete-chain'
    commands['flush nat table'] = 'iptables --table nat --flush'
    commands['delete nat chain'] = 'iptables --table nat --delete-chain'
    commands['flush mangle table'] = 'iptables --table mangle --flush'
    commands['delete mangle chain'] = 'iptables --table mangle --delete-chain'
    commands['flush raw table'] = 'iptables --table raw --flush'
    commands['delete raw chain'] = 'iptables --table raw --delete-chain'
    commands['flush security table'] = 'iptables --table security --flush'
    commands['delete security chain'] = 'iptables --table security --delete-chain'
    commands['accept input'] = 'iptables --policy INPUT ACCEPT'
    commands['accept forward'] = 'iptables --policy FORWARD ACCEPT'
    commands['accept output'] = 'iptables --policy OUTPUT ACCEPT'

    # sys._getframe().f_code.co_name is the function name.
    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands

def initialize_basic_chains() -> dict:
    r"""Apply some basic rules for a single machine."""
    # https://wiki.archlinux.org/index.php/Simple_stateful_firewall#Firewall_for_a_single_machine
    #
    # Copyright (C) 2020 Arch Wiki contributors.
    # Permission is granted to copy, distribute and/or modify this document
    # under the terms of the GNU Free Documentation License, Version 1.3
    # or any later version published by the Free Software Foundation;
    # with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    # A copy of the license is included in the section entitled "GNU
    # Free Documentation License".
    commands = dict()

    # Output traffic is NOT filtered.
    commands['output chain']='iptables --policy OUTPUT ACCEPT'

    # Create two user defined chains that will define tcp an udp protocol rules later.
    commands['tcp chain']='iptables --new-chain TCP'
    commands['udp chain']='iptables --new-chain UDP'

    # For a single machine, however, we simply set the policy of the FORWARD chain to DROP and move on
    commands['drop forward'] = 'iptables --policy FORWARD DROP'

    # The first rule added to the INPUT chain will allow traffic that belongs
    # to established connections, or new valid traffic that is related to these
    # connections such as ICMP errors, or echo replies.
    commands['allow realted established'] = 'iptables --append INPUT --match conntrack --ctstate RELATED,ESTABLISHED --jump ACCEPT'

    # loopback interface INPUT traffic enabled for ping and debugging stuff.
    commands['loopback'] = 'iptables --append INPUT --in-interface lo --jump ACCEPT'

    # Drop all invalid INPUT (i.e. damaged) packets.
    # To do this connection must be tracked (conntrack)
    # and connection state (cstate) is set to INVALID.
    commands['invalid input'] = 'iptables --append INPUT --match conntrack --ctstate INVALID --jump DROP'

    # Allow icmp type 8 (i.e. ping) to all interfaces.
    commands['ping'] = 'iptables --append INPUT --protocol icmp --icmp-type 8 --match conntrack --ctstate NEW --jump ACCEPT'

    # TCP snd UDP chains are connected to INPUT chains.
    # These two user-defined chains will manage the ports.
    # Remember that tcp uses SYN to initialize a connection, unlike UDP
    commands['connect tcp chain'] = 'iptables --append INPUT --protocol tcp --syn -m conntrack --ctstate NEW --jump TCP'
    commands['connect udp chain'] = 'iptables --append INPUT --protocol udp -m conntrack --ctstate NEW --jump UDP'

    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands

def initialize_logging_chain() -> dict:
    r"""Create the logging chain."""
    # https://wiki.archlinux.org/index.php/Iptables#Logging
    #
    # Copyright (C) 2020 Arch Wiki contributors.
    # Permission is granted to copy, distribute and/or modify this document
    # under the terms of the GNU Free Documentation License, Version 1.3
    # or any later version published by the Free Software Foundation;
    # with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    # A copy of the license is included in the section entitled "GNU
    # Free Documentation License".
    commands = dict()

    commands['logging chain']='iptables --new-chain LOGGING'
    commands['connect logging chain'] = 'iptables --append INPUT --jump LOGGING'
    commands['logging limit'] = 'iptables --append LOGGING --match limit --limit 2/hour --limit-burst 10 --jump LOG'

    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands

def initialize_blocking_rules(drop_packets: bool=True, logging: bool=True) -> dict:
    r"""Initialize blocking rules."""
    # https://wiki.archlinux.org/index.php/Simple_stateful_firewall#Firewall_for_a_single_machine
    #
    # Copyright (C) 2020 Arch Wiki contributors.
    # Permission is granted to copy, distribute and/or modify this document
    # under the terms of the GNU Free Documentation License, Version 1.3
    # or any later version published by the Free Software Foundation;
    # with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    # A copy of the license is included in the section entitled "GNU
    # Free Documentation License".
    commands = dict()

    if logging:
        chain = 'LOGGING'
    else:
        chain = 'INPUT'
    if drop_packets:
        # Drop everything.
        commands['drop'] = 'iptables --append ' + chain + ' --jump DROP'
    else:
        # RFC compilant.
        commands['rfc tcp'] = 'iptables --append ' + chain + ' --protocol tcp --jump REJECT --reject-with tcp-rst'
        commands['rfc udp'] = 'iptables --append ' + chain + ' --protocol udp --jump REJECT --reject-with icmp-port-unreachable'
        # Other protocols are usually not used, so REJECT those packets with icmp-proto-unreachable.
        commands['proto unreachable'] = 'iptables --append ' + chain + ' --jump REJECT --reject-with icmp-proto-unreachable'

    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands


def set_accepted_rules(ports: dict, accepted_ips: dict) -> dict:
    r"""Set accepted rules."""
    assert_input_ports_struct(ports)
    assert_accepted_ips_struct(accepted_ips)

    commands = dict()
    # O(ports*chains*ips) <= O(ips^3) because of how this script works.
    i = 0
    for port in ports:
        source = ports[port]['source']
        ips = accepted_ips[source]
        chains, protocols = get_chains_and_protocols(ports[port]['protocol'])
        for w, chain in enumerate(chains):
            for ip in ips:
                commands[str(i)] = generate_accepted_rule_command(chain, protocols[w], port, ip)
                i += 1

    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands


def set_patch_rules(rules: list) -> dict:
    r"""Pass raw commands directly."""
    for r in rules:
        assert isinstance(r, str)

    commands = dict()
    for i, rule in enumerate(rules):
        commands[str(i)] = rule

    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands

def initialize_drop_rules() -> dict:
    r"""Initialize drop rules."""
    commands = dict()
    commands['drop'] = 'iptables --policy INPUT DROP'

    fix_dict_keys(commands, sys._getframe().f_code.co_name, '__')
    return commands


#########
# Utils #
#########

def get_chains_and_protocols(protocol: str) -> tuple:
    r"""Compute the iptables chain and protocol values."""
    assert protocol in ['tcp', 'udp', 'all']

    chains = list()
    protocols = list()
    if protocol == 'tcp':
        chains.append('TCP')
        protocols.append('tcp')
    elif protocol == 'udp':
        chains.append('UDP')
        protocols.append('udp')
    elif protocol == 'all':
        chains.append('TCP')
        chains.append('UDP')
        protocols.append('tcp')
        protocols.append('udp')

    return chains, protocols

def generate_accepted_rule_command(chain: str, protocol: str, port: str, remote_ip: str) -> str:
    r"""Generate a single command for the accepted rules."""
    check_port(port)
    check_ip_address(remote_ip)

    return ('iptables --append ' + chain + ' --protocol '
                    + protocol + ' --dport ' + port + ' --source ' + remote_ip
                    + ' --jump ACCEPT')

def fix_dict_keys(dictionary: dict, prefix: str, separator: str):
    r"""Fix the keys of a dictionary by adding a prefix and separator."""
    d = copy.deepcopy(dictionary)
    for key in d:
        dictionary[prefix + separator + key] = d[key]
        del dictionary[key]

def load_zone_file(zone_file: str) -> list:
    r"""Load zone file."""
    zones = list()
    with open(zone_file, 'r') as f:
        line = f.readline().strip()
        while line:
            check_ip_address(line)
            zones.append(line)
            line = f.readline().strip()

    return zones

def load_zone_files(zone_files: list) -> list:
    r"""Load all the zone files content in a flat data structure."""
    for zf in zone_files:
        assert isinstance(zf, str)

    zones = list()
    for zf in zone_files:
        zones += load_zone_file(zf)

    return zones

def get_filename_from_url(url: str) -> str:
    r"""Use some tricks to get the filemame from a URL."""
    return pathlib.PurePath(urllib.parse.urlparse(url).path).name

def download_zone_file(url: str, dst_directory: str) -> str:
    r"""Save the zone file."""
    filename = get_filename_from_url(url)
    pathlib.Path(dst_directory).mkdir(mode=0o700, parents=True, exist_ok=True)
    full_path = str(pathlib.Path(dst_directory, filename))
    try:
        r = requests.get(url)
        with open(full_path, 'w') as f:
            f.write(r.text)
    except requests.ConnectionError:
        pass

    return full_path

def download_zone_files(urls: list, cache_directory: str) -> list:
    r"""Download multiple zone files."""
    for u in urls:
        assert isinstance(u, str)

    files = list()
    for u in urls:
        files.append(download_zone_file(u, cache_directory))

    return files

def update_accepted_ips_structure(accepted_ips: dict, zones: list):
    r"""Update some data structures."""
    assert_accepted_ips_struct(accepted_ips)
    assert_zones_struct(zones)

    accepted_ips['wan'] = zones
    accepted_ips['all'] = accepted_ips['lan'] + accepted_ips['wan']

def get_packet_policy(invalid_packet_policy: str) -> bool:
    r"""Update a variable."""
    assert invalid_packet_policy in ['polite','rude']

    drop = True
    if invalid_packet_policy == 'rude':
        drop = True
    elif invalid_packet_policy == 'polite':
        drop = False
    return drop

def run_commands(commands: dict, dry_run: bool=False):
    r"""Execute and print the commands' output."""
    for c in commands:
        command_string= str()
        if dry_run:
            command_string += '/bin/echo '
        command_string += commands[c]
        command = shlex.split(command_string)
        print (subprocess.run(command, capture_output=True, check=True, timeout=30).stdout.decode('UTF-8'),end='')

##############
# Assertions #
##############

def check_ip_address(ip: str):
    r"""Verify that we are dealing with a network address."""
    ipaddress.ip_network(ip, strict=True)

def check_port(port: str):
    r"""Check that the input port is a valid port number."""
    assert port.isdigit()
    assert int(port) >= 0 and int(port) <= (2**16)-1

def assert_zones_struct(zones: list):
    r"""Check that the data structure is a list of ip addresses."""
    for z in zones:
        assert isinstance(z, str)
        check_ip_address(z)

def assert_accepted_ips_struct(accepted_ips: dict):
    r"""Check that the data structure is a list of ip addresses."""
    for ips in accepted_ips:
        assert isinstance(accepted_ips[ips], list)
        for j in accepted_ips[ips]:
            assert isinstance(j, str)
            check_ip_address(j)

def assert_input_ports_struct(ports: dict):
    r"""Check that the data structure is correct."""
    for port in ports:
        check_port(port)
        assert isinstance(ports[port], dict)
        assert 'source' in ports[port]
        assert 'protocol' in ports[port]
        assert ports[port]['source'] in ['lan','wan','all']

############
# Pipeline #
############

if __name__ == '__main__':
    if os.getuid() != 0:
        raise UserNotRoot

    # Load the configuration.
    configuration_file = shlex.quote(sys.argv[1])
    with open(configuration_file, 'r') as f:
        configuration = yaml.load(f, Loader=yaml.BaseLoader)
    dry_run = configuration['dry run']
    cache_directory = configuration['cache directory']
    zone_files = configuration['accepted ips']['wan']
    accepted_ips = dict()
    accepted_ips['lan'] = configuration['accepted ips']['lan']
    accepted_ips['wan'] = list()
    patch_rules = configuration['patch rules']
    input_ports = configuration['input ports']
    logging = configuration['logging enabled']
    invalid_packet_policy = configuration['invalid packet policy']
    drop_packets = get_packet_policy(invalid_packet_policy)

    # Get the data.
    zones = load_zone_files(download_zone_files(zone_files, cache_directory))
    update_accepted_ips_structure(accepted_ips, zones)

    # Apply the rules.
    reset = reset_rules()
    basic_chains = initialize_basic_chains()
    logging_chain = initialize_logging_chain()
    blocking_rules = initialize_blocking_rules(drop_packets, logging)
    rules = set_accepted_rules(input_ports, accepted_ips)
    patch = set_patch_rules(patch_rules)
    drop_by_default = initialize_drop_rules()

    # Merge the rules.
    commands = {**reset, **basic_chains,
        **logging_chain, **blocking_rules, **rules, **patch, **drop_by_default}

    # Apply the rules.
    run_commands(commands, dry_run)
