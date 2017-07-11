# This will just contain a lot of precanned show commands
from getinput import getInput as getinput

# There is a mapping list of numbers to pre-canned reports, it is as follows:
# 1 = findHostByMAC

# Some global variables we can reference between loops for various commands
# This is a list of mac addresses used for different commands
macAddresses = []

def printCommandNumbers():
    print('''
    Precanned-show commands list:\n
    1 - find a host by MAC address, requires a mac address to be passed
    ''')

def getMAC():
    mac = getinput(prompt='Enter the MAC address find\n'
                          'Brocade format is xxxx.xxxx.xxxx:\n'
                          'Cisco IOS format is xxxx.xxxx.xxxx\n'
                   )
    macAddresses.append(mac)

# This command takes the command number passed to it and runs the command
# It is basically the interface into selecting the command
def commandToUse(toUse='1', device_type='device_type', counter=0):

    # 1 corresponds to find host by MAC address
    if toUse == '1':

        # Get the mac address to use
        # Only ask if the counter is at 0
        if counter == 0:
            getMAC()

        # We call the actual function now
        returnCmd = findHostByMAC(device_type=device_type, mac=macAddresses[0])
        return returnCmd

def findHostByMAC(device_type='brocade_fastiron', mac='macPlaceholder'):
    # We need to know how to format our commands..
    if device_type == 'brocade_fastiron':
        cmd = 'show mac-address {mac}'.format(mac=mac)
        return cmd
    elif device_type == 'cisco_ios':
        cmd = 'show mac address-table address {mac}'.format(mac=mac)
        return cmd


