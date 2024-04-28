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


# FIXME: I think that's the way to make the topology
class FinalTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, n, **opts):
        Topo.__init__(self, **opts)
        # adding the 3 P4Switches
        switch1 = self.addSwitch('s1',
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port) 
        
        switch2 = self.addSwitch('s2',
                        sw_path = sw_path,
                        json_path = json_path,
                        thrift_port = thrift_port+1)

        switch3 = self.addSwitch('s3',
                        sw_path = sw_path,
                        json_path = json_path,
                        thrift_port = thrift_port+2)
        for i in range(3):
            # adding host and link with the right mac and ip addrs
            if i == 0:
                host = self.addHost('h%d' % (i + 1),
                                ip = "10.0.1.1/24" ,
                                mac = "00:04:00:00:00:01")
                self.addLink(host, switch1, addr2="00:aa:bb:00:00:01")
            elif i == 1:
                host = self.addHost('h%d' % (i + 1),
                                ip = "10.0.6.1/24" ,
                                mac = "00:04:00:00:00:03")
                self.addLink(host, switch2, addr2="00:aa:dd:00:00:02")
            else: 
                host = self.addHost('h%d' % (i + 1),
                                ip = "10.0.3.1/24" ,
                                mac = "00:04:00:00:00:02")
                self.addLink(host, switch3, addr2="00:aa:cc:00:00:01")


        self.addLink(switch1, switch2, addr1="00:aa:bb:00:00:03", addr2="00:aa:dd:00:00:01")
        self.addLink(switch1, switch3, addr1="00:aa:bb:00:00:02" , addr2="00:aa:cc:00:00:02")
        self.addLink(switch2, switch3, addr1="00:aa:dd:00:00:03" , addr2="00:aa:cc:00:00:03")

        

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
                  switch = P4Switch,
                  controller = None)

    # Here, the mininet will use the constructor (__init__()) of the P4Switch class, 
    # with the arguments passed to the SingleSwitchTopo class in order to create 
    # our software switch.
    net.start()

    # # an array of the mac addrs from the switch
    # sw1_mac = ["00:aa:bb:00:00:01","00:aa:bb:00:00:02","00:aa:bb:00:00:03"]
    # sw2_mac = ["00:aa:dd:00:00:02","00:aa:dd:00:00:03","00:aa:dd:00:00:01"]
    # sw3_mac = ["00:aa:cc:00:00:01","00:aa:cc:00:00:03","00:aa:cc:00:00:02"]
    # an array of the ip addrs from the switch 
    # they are only used to define defaultRoutes on hosts 
    # sw1_addr = ["10.0.1.254","10.0.2.254","10.0.5.251"]
    # sw2_addr = ["10.0.6.250","10.0.4.250","10.0.5.250"]
    # sw3_addr = ["10.0.3.253","10.0.4.252","10.0.2.253"]

    # h.setARP() populates the arp table of the host
    # h.setDefaultRoute() sets the defaultRoute for the host
    # populating the arp table of the host with the switch ip and switch mac
    # avoids the need for arp request from the host

    gateway_mac_r1 = "00:aa:bb:00:00:01"
    gateway_ip_r1 = "10.0.1.254"
    gateway_mac_r2 = "00:aa:dd:00:00:02"
    gateway_ip_r2 = "10.0.6.250"
    gateway_mac_r3 = "00:aa:cc:00:00:02"
    gateway_ip_r3 = "10.0.3.253"


    h11 = net.get('h1')
    h11.setARP(gateway_ip_r1,gateway_mac_r1)
    h11.setDefaultRoute("dev eth0 via %s" % gateway_ip_r1)


    h11 = net.get('h2')
    h11.setARP(gateway_ip_r2,gateway_mac_r2)
    h11.setDefaultRoute("dev eth0 via %s" % gateway_ip_r2)

    
    h11 = net.get('h3')
    h11.setARP(gateway_ip_r3,gateway_mac_r3)
    h11.setDefaultRoute("dev eth0 via %s" % gateway_ip_r3)

    for n in range(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()

    sleep(1)  # time for the host and switch confs to take effect

    print("Ready !")

    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
