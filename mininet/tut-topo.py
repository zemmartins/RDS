#!/usr/bin/env python3
# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
############################################################################
# RDS-TUT jfpereira - Read all comments from this point on !!!!!!
############################################################################
# This code is given in 
# https://github.com/p4lang/behavioral-model/blob/main/mininet/1sw_demo.py
# with minor adjustments to satisfy the requirements of RDS-TP3. 
# This script works for a topology with one P4Switch connected to 253 P4Hosts. 
# In this TP3, we only need 1 P4Switch and 2 P4Hosts.
# The P4Hosts are regular mininet Hosts with IPv6 suppression.
# The P4Switch it's a very different piece of software from other switches 
# in mininet like OVSSwitch, OVSKernelSwitch, UserSwitch, etc.
# You can see the definition of P4Host and P4Switch in p4_mininet.py
###########################################################################

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSSwitch
from mininet.node import OVSKernelSwitch
import subprocess


from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep

# If you look at this parser, it can identify 4 arguments
# --behavioral-exe, with the default value 'simple_switch'
## this indicates that the arch of our software switch is the 'simple_switch'
## and any p4 program made for this arch needs to be compiled against de 'v1model.p4'
# --thrift-port, with the default value of 9090, which is the default server port of
## a thrift server - the P4Switch instantiates a Thrift server that allows us
## to communicate our P4Switch (software switch) at runtime
# --num-hosts, with default value 2 indicates the number of hosts...
# --json, is the path to JSON config file - the output of your p4 program compilation
## this is the only argument that you will need to pass in orther to run the script
parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", default='simple_switch')
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=3)
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)

args = parser.parse_args()


class FinalTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, n, **opts):
        Topo.__init__(self, **opts)
        # adding the 3 P4Switches
        router1 = self.addSwitch('r1',
                                cls = P4Switch,
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port) 
        
        router2 = self.addSwitch('r2',
                                cls = P4Switch,
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port+1)

        router3 = self.addSwitch('r3',
                                cls = P4Switch,
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port+2)
        
        switch1 = self.addSwitch('s1',cls = OVSSwitch)

        switch2 = self.addSwitch('s2',cls = OVSSwitch)

        switch3 = self.addSwitch('s3',cls = OVSSwitch)

        # LAN 1
        host11 = self.addHost('h11',
                        ip = "10.0.1.100/24" ,
                        mac = "00:04:00:00:00:01")
        self.addLink(host11, switch1, addr2="00:aa:00:00:00:11")

        server11 = self.addHost('server11',
                        ip = "10.0.1.10/24" ,
                        mac = "00:04:00:00:00:20")
        self.addLink(server11, switch1, addr2="00:aa:00:00:00:12")
        
        server12 = self.addHost('server12',
                        ip = "10.0.1.20/24" ,
                        mac = "00:04:00:00:00:30")
        self.addLink(server12, switch1, addr2="00:aa:00:00:00:13")

        # LAN 2
        host21 = self.addHost('h21',
                        ip = "10.0.2.100/24" ,
                        mac = "00:04:00:00:00:03")
        self.addLink(host21, switch2, addr2="00:aa:00:00:00:21")

        server21 = self.addHost('server21',
                        ip = "10.0.2.10/24" ,
                        mac = "00:04:00:00:00:40")
        self.addLink(server21, switch2, addr2="00:aa:00:00:00:22")
        
        server22 = self.addHost('server22',
                        ip = "10.0.2.20/24" ,
                        mac = "00:04:00:00:00:50")
        self.addLink(server22, switch2, addr2="00:aa:00:00:00:23")

        # LAN 3

        host31 = self.addHost('h31',
                        ip = "10.0.3.100/24" ,
                        mac = "00:04:00:00:00:02")
        self.addLink(host31, switch3, addr2="00:aa:00:00:00:31")

        server31 = self.addHost('server31',
                        ip = "10.0.3.10/24" ,
                        mac = "00:04:00:00:00:60")
        self.addLink(server31, switch3, addr2="00:aa:00:00:00:32")
        
        server32 = self.addHost('server32',
                        ip = "10.0.3.20/24" ,
                        mac = "00:04:00:00:00:70")
        self.addLink(server32, switch3, addr2="00:aa:00:00:00:33")


        # Ligacoes entre routers

        self.addLink(router1, router2, addr1="00:aa:bb:00:00:03", addr2="00:aa:dd:00:00:01")
        self.addLink(router1, router3, addr1="00:aa:bb:00:00:02", addr2="00:aa:cc:00:00:02")
        self.addLink(router2, router3, addr1="00:aa:dd:00:00:03", addr2="00:aa:cc:00:00:03")

        # Ligacoes entre switches e routers

        self.addLink(router1, switch1, addr1="00:aa:bb:00:00:01", addr2="00:aa:00:00:00:10")
        self.addLink(router2, switch2, addr1="00:aa:dd:00:00:02", addr2="00:aa:00:00:00:20")
        self.addLink(router3, switch3, addr1="00:aa:cc:00:00:01", addr2="00:aa:00:00:00:30")



def main():

    num_hosts = args.num_hosts

    topo = FinalTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            num_hosts)

    # the host class is the P4Host
    # the switch class is the P4Switch
    net = Mininet(topo = topo,
                  host = P4Host,
                  controller = None)

    # Here, the mininet will use the constructor (__init__()) of the P4Switch class, 
    # with the arguments passed to the SingleSwitchTopo class in order to create 
    # our software switch.
    net.start()

    commands = [
        'sudo ovs-ofctl add-flow s1 in_port=1,actions=normal',
        'sudo ovs-ofctl add-flow s1 in_port=2,actions=normal',
        'sudo ovs-ofctl add-flow s1 in_port=3,actions=normal',
        'sudo ovs-ofctl add-flow s1 in_port=4,actions=normal',
        'sudo ovs-ofctl add-flow s2 in_port=1,actions=normal',
        'sudo ovs-ofctl add-flow s2 in_port=2,actions=normal',
        'sudo ovs-ofctl add-flow s2 in_port=3,actions=normal',
        'sudo ovs-ofctl add-flow s2 in_port=4,actions=normal',
        'sudo ovs-ofctl add-flow s3 in_port=1,actions=normal',
        'sudo ovs-ofctl add-flow s3 in_port=2,actions=normal',
        'sudo ovs-ofctl add-flow s3 in_port=3,actions=normal',
        'sudo ovs-ofctl add-flow s3 in_port=4,actions=normal'
    ]

    # Execute each command in the list
    for cmd in commands:
        print('Running ...')
        subprocess.call(cmd, shell=True)

    subprocess.call('cd commands && simple_switch_CLI --thrift-port 9090 < commandsR1.txt && simple_switch_CLI --thrift-port 9091 < commandsR2.txt && simple_switch_CLI --thrift-port 9092 < commandsR3.txt', shell=True)
    print('Done with the routers!!')




    # h.setARP() populates the arp table of the host
    # h.setDefaultRoute() sets the defaultRoute for the host
    # populating the arp table of the host with the switch ip and switch mac
    # avoids the need for arp request from the host

    gateway_mac_r1 = "00:aa:bb:00:00:01"
    gateway_ip_r1  = "10.0.1.254"
    gateway_mac_r2 = "00:aa:dd:00:00:02"
    gateway_ip_r2  = "10.0.2.250"
    gateway_mac_r3 = "00:aa:cc:00:00:01"
    gateway_ip_r3  = "10.0.3.253"

    
    h11 = net.get('h11')
    h11.setARP(gateway_ip_r1,gateway_mac_r1)
    h11.setDefaultRoute("dev eth0 via %s" % gateway_ip_r1)

    srv11 = net.get('server11')
    srv11.setARP(gateway_ip_r1,gateway_mac_r1)
    srv11.setDefaultRoute("dev eth0 via %s" % gateway_ip_r1)
    
    srv12 = net.get('server12')
    srv12.setARP(gateway_ip_r1,gateway_mac_r1)
    srv12.setDefaultRoute("dev eth0 via %s" % gateway_ip_r1)


    h21 = net.get('h21')
    h21.setARP(gateway_ip_r2,gateway_mac_r2)
    h21.setDefaultRoute("dev eth0 via %s" % gateway_ip_r2)

    srv21 = net.get('server21')
    srv21.setARP(gateway_ip_r2,gateway_mac_r2)
    srv21.setDefaultRoute("dev eth0 via %s" % gateway_ip_r2)

    srv22 = net.get('server22')
    srv22.setARP(gateway_ip_r2,gateway_mac_r2)
    srv22.setDefaultRoute("dev eth0 via %s" % gateway_ip_r2)

    
    h31 = net.get('h31')
    h31.setARP(gateway_ip_r3,gateway_mac_r3)
    h31.setDefaultRoute("dev eth0 via %s" % gateway_ip_r3)

    srv31 = net.get('server31')
    srv31.setARP(gateway_ip_r3,gateway_mac_r3)
    srv31.setDefaultRoute("dev eth0 via %s" % gateway_ip_r3)

    srv32 = net.get('server32')
    srv32.setARP(gateway_ip_r3,gateway_mac_r3)
    srv32.setDefaultRoute("dev eth0 via %s" % gateway_ip_r3)

    sleep(1)  # time for the host and switch confs to take effect

    print("Ready !")   

    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
