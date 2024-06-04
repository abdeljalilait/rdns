#!/bin/bash

file=$(python rdns.py $1 $2 $3)

cat named.conf > /etc/named.conf
cat named.conf.zones > /etc/named.conf.zones
cat $file > /var/named/$file
named-checkconf /etc/named.conf
iptables -A INPUT -p tcp --dport 53 -j ACCEPT
iptables -A INPUT -p udp --dport 53 -j ACCEPT
service named restart