import threading
import paramiko
import subprocess
import getpass
import sys
import time
import os
import getopt
import socket
from sys import argv
from netmiko import ConnectHandler
import re
import time
import json
import pprint
from ipaddress import ip_network 

# Promt symbol
prompt = '\t# '

def clear_screen():
    os.system('clear')

def get_user_credentials():
	global username
	global password
	global enable_password
	print "\tEnter Username: "
	username = raw_input(prompt)
	print "\tEnter Password: "
	password = getpass.getpass('\tPassword:')
	print "\tEnter Enable Password: "
	enable_password = getpass.getpass('\tEnable Password:')

def ssh_command(ip):
	clear_screen()
	global shell
	try:
		print "\tConnecting to: ", ip
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh_client.connect(ip, username=username, password=password, allow_agent=False, look_for_keys=False)
		shell = ssh_client.invoke_shell(height=1240)
		shell.send('en\n')
		time.sleep(1)
		shell.send(enable_password)
		time.sleep(1)
		shell.send('\n')
		time.sleep(1)
		shell.send('terminal length 0\n')
		time.sleep(1)
		shell.send('show run | inc interface | ip address')
		shell.send('\n')
		time.sleep(1)
		output = shell.recv(50000)
		return output
	except paramiko.SSHException:
		print '\tAuthenctication Failure'
	except socket.error:
		print '\tUnable to connect to: ', ip
	ssh_client.close()

def netmask_to_cidr(netmask):
    '''
    :param netmask: netmask ip addr (eg: 255.255.255.0)
    :return: equivalent cidr number to given netmask ip (eg: 24)
    '''
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])

def sameNetwork(IP1, IP2):

    a = ip_network(IP1, strict = False).network_address
    b = ip_network(IP2, strict = False).network_address
    if(a == b):
        return True

    else:
        return False

def router_interfaces(cli_output):
	interface = {'name':[], 'ip_address':[]} # interfaces dictionary with key:name value:ip_address
	int_name_pattern = "^interface" # re pattern to recognise line that starts with interface
	pattern_int = re.compile(int_name_pattern)
	int_ip_pattern = "^ip" 
	pattern_ip = re.compile(int_ip_pattern) # re pattern to recognise line that starts with ip
	global router_ints
	router_ints = {}

	for line in cli_output.rsplit('\n'):
		if pattern_int.search(line):
			interface['name'] = line.split()[1] # if pattern exists take the interface name
		elif re.match(r'^ ip address', line): # the other expected line is the one that has ip address
			ip_mask = line.split("address",1)[1] # here we remove the ip address text
			ip_subnet_mask = ip_mask.split() # here we separate ip from mask
			if len(ip_subnet_mask) > 1:
				for i in range(len(ip_subnet_mask)):
					mask=(netmask_to_cidr(ip_subnet_mask[1])) # convert mask to CIDR
					ip = ip_subnet_mask[0] # take the ip address and save it to variable ip
					ip_address = str(ip) + "/" + str(mask) # make it string since it complains for int
					interface['ip_address'] = ip_address # add the value to the interface dictionary
					router_ints[interface['name']] = interface['ip_address'] # append every interfaceto the router_interfaces dictionary
			else:
				pass
		else:
			pass
	return router_ints

file1 = open('hosts', 'r')
Lines = file1.readlines()
topology_dict = {'nodes': [], 'links': []}

#get_user_credentials()
username = 'renos'
password = "cisco"
enable_password = 'cisco'
for line in Lines: # read file to compare ip
	line.rstrip('\n')
	print "\tConnecting to: ", line
	ip = line.rstrip('\n')
	output = ssh_command(ip)
	#print output
	intf = router_interfaces(output)
	v = json.dumps(intf, indent=4)
	ip = ip + ".temp_json"
	f = open(ip,"w")
	f.write(v)
	f.close()
