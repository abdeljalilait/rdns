from sys import argv
from json import loads
from random import randint


named_conf = """
//
// named.conf
//
// Provided by Red Hat bind package to configure the ISC BIND named(8) DNS
// server as a caching only nameserver (as a localhost DNS resolver only).
//
// See /usr/share/doc/bind*/sample/ for example named configuration files.
//
// See the BIND Administrator's Reference Manual (ARM) for details about the
// configuration located in /usr/share/doc/bind-{version}/Bv9ARM.html
options {
    listen-on port 53 { 127.0.0.1;[ip]; };
    directory       "/var/named";
    dump-file       "/var/named/data/cache_dump.db";
    statistics-file "/var/named/data/named_stats.txt";
    pid-file "/run/named/named.pid";
};

view "external" {
    match-clients { any; };
    recursion no;
    include "/etc/named.conf.zones";
};
"""

zones = """
zone  [subnet].in-addr.arpa. {
    type master;
    file "/var/named/[subnet].in-addr.arpa";
};
"""
named_zones_path = "named.conf.zones"

zones_file = "[subnet].in-addr.arpa"


rdns_records = """
$TTL 172900
[subnet].in-addr.arpa.     SOA      [ns1].  [ns2]. (
        [rand]   ; serial
        3600     ;refresh
        900      ;retry
        1209600  ;expire   2 weeks
        43200    ; selector1 TTL
)

[subnet].in-addr.arpa. IN      NS       [ns1].
[subnet].in-addr.arpa.  IN      NS       [ns2].
"""

def validate_ip_address(address):
    parts = address.split(".")

    if len(parts) != 4:
        print("IP address {} is not valid".format(address))
        return False

    for part in parts:
        if not isinstance(int(part), int):
            print("IP address {} is not valid".format(address))
            return False

        if int(part) < 0 or int(part) > 255:
            print("IP address {} is not valid".format(address))
            return False
    return True

if __name__ == '__main__':
    # read records file which is domain;ip seperated by semicolon
    file1 = open('records.txt', 'r')
    Lines = file1.readlines()
    subnet = argv[1]
    ip = argv[2]
    nameservers = loads(argv[3])
    if validate_ip_address(ip):
        named_conf = named_conf.replace("[ip]", ip)
        subnet = subnet.split('/') # "195.154.22.57/27"
        mask = subnet[1] #27
        network = subnet[0].split('.')[-1] #57
        subnet =  '.'.join(subnet[0].split('.')[2::-1]) #22.154.195
        subnet = network + '-' + mask + '.' + subnet # 32-27.22.154.195

        #replace the subnet
        zones = zones.replace("[subnet]", subnet)
        zones_file = zones_file.replace("[subnet]", subnet)
        rdns_records = rdns_records.replace("[subnet]", subnet)

        #replace nameservers
        rdns_records = rdns_records.replace("[ns1]", nameservers[0])
        rdns_records = rdns_records.replace("[ns2]", nameservers[1])
        #create random number for serial
        rdns_records = rdns_records.replace("[rand]", str(randint(100, 100000)))

        # open named config
        named_config_file = open("named.conf", "w")
        # write to it
        named_config_file.write(named_conf)

        # open zones file
        named_zones_file = open(named_zones_path, "w") #named_zones_path
        # write to it
        named_zones_file.write(zones)

        # open rdns records for append
        records_file = open(zones_file, "a")
        #delete file content
        records_file.truncate(0)
        # write to it
        records_file.write(rdns_records)

        count = 0
        for line in Lines:
            count += 1
            domain , ip = line.strip().split(';')
            network = ip.split('.')[-1]
            records_file.write(network + '.' + subnet + '.in-addr.arpa.' + ' IN PTR ' + domain + '.\n')

        # return dynamic rdns file name to stdout
        print(zones_file)


