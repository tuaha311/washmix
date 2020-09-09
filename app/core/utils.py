from netaddr import IPAddress, IPNetwork


def ip_in_white_list(ip, network_list):
    ip = IPAddress(ip)
    network_list = [IPNetwork(network) for network in network_list]

    return any(ip in network for network in network_list)
