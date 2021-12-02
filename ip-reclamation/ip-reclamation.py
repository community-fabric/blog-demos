from ipfabric import IPFClient
from ipaddress import IPv4Interface, IPv4Network, AddressValueError, IPv4Address
from tabulate import tabulate
import re
from json import dumps

net = IPv4Network('192.168.0.0/16')

regex = re.compile("(range )?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
                   "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2})?")


def ips(start, end):
    '''Return IPs in IPv4 range, inclusive.'''
    start_int = int(IPv4Address(start).packed.hex(), 16)
    end_int = int(IPv4Address(end).packed.hex(), 16)
    return [IPv4Address(ip).exploded for ip in range(start_int, end_int)]


def format_network(match):
    returned_networks = list()
    for n in match:
        network = n.group().split(' ')
        if 'range' in n.group():
            returned_networks.extend(ips(network[1], network[2]))
        elif len(network) > 1:
            if re.search(r'^0', network[1]):
                returned_networks.append(
                    network[0] + '/' + str(IPv4Address._prefix_from_ip_int(int(IPv4Address(network[1])) ^ (2**32-1)))
                )
            elif re.search(r'^/', network[1]):
                returned_networks.append(network[0] + network[1])
            else:
                returned_networks.append(
                    network[0] + '/' + str(IPv4Address._prefix_from_ip_int(int(IPv4Address(network[1]))))
                )
        else:
            returned_networks.append(network[0])
    return returned_networks


def check_network(data):
    match = list(regex.finditer(data))
    for network in format_network(match):
        try:
            network = IPv4Interface(network)
            if net.overlaps(network.network) and str(network.network.network_address) != '0.0.0.0':
                raise StopIteration
        except AddressValueError:
            pass


def check_policy(data):
    if isinstance(data, str):
        check_network(data)
    elif isinstance(data, list):
        for i in data:
            check_policy(i)
    elif isinstance(data, dict):
        for j, k in data.items():
            check_network(j)
            check_policy(k)


def check_named_values(named_values):
    filtered_values = set()
    if named_values and 'numberSet' in named_values:
        for name, value in named_values['numberSet'].items():
            try:
                check_network(value['original'])
            except StopIteration:
                filtered_values.add(name)
    return filtered_values


def check_named_tests(named_tests, named_values):
    filtered_tests = set()
    if not named_tests:
        return filtered_tests
    for name, test in named_tests.items():
        test_str = dumps(test)
        for value in named_values:
            if value in test_str:
                filtered_tests.add(name)
                break
        else:
            try:
                check_policy(test)
            except StopIteration:
                filtered_tests.add(name)
    return filtered_tests


def recheck_named_tests(named_tests, current):
    if not named_tests or current:
        return current
    for name, test in named_tests.items():
        test_str = dumps(test)
        for value in named_values:
            if value in test_str:
                current.add(name)
                break
    return current


def check_zone_policy(rules, search_strings):
    rule = dumps(rules)
    for string in search_strings:
        if string in rule:
            raise StopIteration


if __name__ == '__main__':
    ipf = IPFClient(snapshot_id='d3bd033e-1ba6-4b27-86f5-18824a1a495e')
    # IPFClient('https://demo3.ipfabric.io/', token='TOKEN') if you are not using IPF_URL and IPF_TOKEN env. variables

    acls = ipf.security.search_acl_policies()
    sn = {a['sn'] for a in acls}
    acl_matches = list()
    for serial in sn:
        policies = ipf.security.get_policy(serial)
        for name, policy in policies.machine_acl.items():
            if policy.hidden:
                continue
            try:
                check_policy(policy.rules)
            except StopIteration:
                acl_matches.append([policies.hostname, name])

    print(f"{len(acl_matches)} ACL Matches:")
    print(tabulate(acl_matches, headers=["hostname", "name"]))

    print()

    zones = ipf.security.search_zone_policies()
    sn = {a['sn'] for a in zones}
    zone_matches = list()
    for serial in sn:
        policies = ipf.security.get_policy(serial)
        named_values = check_named_values(policies.named_values)
        named_tests = check_named_tests(policies.named_tests, named_values)
        named_tests = recheck_named_tests(policies.named_tests, named_tests)
        search_strings = set.union(named_tests, named_values)
        if named_values:
            print()
        for name, policy in policies.machine_zones.items():
            if policy.hidden:
                continue
            try:
                check_zone_policy(policy.rules, search_strings)
                check_policy(policy.rules)
            except StopIteration:
                zone_matches.append([policies.hostname, name])

    print(f"{len(zone_matches)} Zone Matches:")
    print(tabulate(zone_matches, headers=["hostname", "name"]))
