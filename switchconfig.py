#!/usr/bin/env python

# This will ensure that is users are using python2, the print function will work like a python3
# And that if they are doing integer division that it will not floor divide but return a
# Decimal point if necessary like python3
from __future__ import print_function, division

# Netmiko is how we will get an shell into a device and perform operations
import netmiko
import json
import precannedshow

from datetime import datetime
# getpass is to get password input and not print it on the screen
from getpass import getpass
# This is a class I defined with a custom print to work for python 2 or 3
from getinput import getInput as getinput







class SwitchConfig():

    def __init__(self):
        pass

    # This function's purpose is simply to get the password
    def getPassword(self):
        # To make sure we get a password we will loop until a value is entered
        while True:
            passwd = getpass('Please enter a password to use for the switches:\n')
            # if nothing was entered ask them again!
            if passwd != None:
                return passwd
                break
            else:
                print('Please enter a password for the device {ip}\n'.format(ip=ip))

    # Simply prints a line of ~'s
    def printLine(self):
        print('~' * 79)

    # This prints a spacer between outputs
    def printSpacer(self):
        print('\n\n', '-' * 79, '\n', '*' * 79, '\n', '-' * 79, '\n\n')


    # This command establishes the connection
    def connect(self, ip='none', device_type='none', username='username', password='password',
                cmd='cmd', cmdType='1', precannedNumber='1'):

        # Lets see how long the whole process takes too
        start = datetime.now()

        # We need to catch any exceptions that may occur
        try:
            connection = netmiko.ConnectHandler(ip=ip, device_type=device_type,
                                                username=username, password=password)

            #This is just for debugging to output the handler of the connection if tshooting
            # print(connection)

            # send a test command
            # Find prompt will append the device name to the output
            self.printLine()


            # If cmdType is 1 or 3 it is a show command
            if cmdType in ['1', '3']:
                self.showCommand(cmd=cmd, connection=connection)
            # If it is type 2 do a config command
            elif cmdType == '2':
                self.configCommand(cmd=cmd, connection=connection)


            # Lets disconnect
            connection.disconnect()

            self.printLine()

            elapsed = datetime.now() - start
            print('Time elapsed to run the command was {time}'.format(time=elapsed))
            self.printSpacer()

        except netmiko.NetMikoAuthenticationException:
            print('Authentication failed for {ip}'.format(ip=ip))

        except netmiko.NetMikoTimeoutException:
            print('Timed out trying to connect to host {ip}'.format(ip=ip))

        except Exception as e:
            print(e)


    # This is the function that handles show commands
    def showCommand(self, cmd='cmd', connection='connectionHandlerPlaceHolder'):
        result = connection.find_prompt() + '\n'
        result += connection.send_command(cmd)
        print(result)

    def configCommand(self, cmd=[], connection='connectionHandlerPlaceHolder'):
        connection.send_config_set(cmd)












# Create an instance of the class switch config
# Only if we call this file directly
if __name__ == '__main__':

    # Create an instance of the class above
    swcfg = SwitchConfig()

    # We will set up a connection handler with Netmiko
    # Lets make a List of dictionaries that has our info in it
    devices = [
                {'ip': '192.168.70.240', 'device_type': 'brocade_fastiron'},
                {'ip': '172.20.2.11', 'device_type': 'cisco_ios'}
        ]

    # Lets ask for the username to use here as well
    username = getinput(prompt='Enter the username to use for the switches:')

    # We're assuming the password is the same for each switch..
    # We need to prompt for the password, we need to pass the ip for
    # output of the cli fields to prompt the user
    password = swcfg.getPassword()


    # Lets see if this is a show command or config command or a precanned command
    while True:
        cmdType = getinput(prompt='Choose the command type you wish to run:\n'
                            'enter 1 for a show command\n'
                            'enter 2 for a config command\n'
                            'enter 3 for a precanned show command'
                        )
        if cmdType not in ['1', '2', '3']:
            print('Enter a valid choice\n')
        else:
            break

    # Here we need to get the number of the pre-canned show report to use
    if cmdType == '3':
        precannedshow.printCommandNumbers()
        toUse = getinput('Enter the command number you want to use from the output above:')

        # Loop counter, used for various purposes
        counter = 0

        for hosts in devices:
            # Because we have to pass the device type into precannedshow we have to
            # define the actual command inside the loop iterating through the list
            # of hosts
            cmd = precannedshow.commandToUse(toUse, device_type=hosts['device_type'], counter=counter)

            # The below was for debugging only
            #print(cmd)

            # For each host defined in the device list of dictionaries lets do the command
            # We pass the current dictionary in the list as kwargs to the function
            swcfg.connect(**hosts, username=username, password=password, cmd=cmd, cmdType=cmdType)

            # increment counter
            counter += 1

    else:
        # Get the command we need to run
        cmd = getinput(prompt='Enter the command to run against the switches:\n')

        for hosts in devices:
            # For each host defined in the device list of dictionaries lets do the command
            # We pass the current dictionary in the list as kwargs to the function
            swcfg.connect(**hosts, username=username, password=password, cmd=cmd, cmdType=cmdType)
















