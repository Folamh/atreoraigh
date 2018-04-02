#!/usr/bin/env bash

PORT=56565
IPADDR='127.0.0.1'

sudo iptables -A INPUT -p udp --dport $PORT -j NFQUEUE --queue-num 1

sudo iptables -A INPUT -p tcp --dport $PORT -j REJECT