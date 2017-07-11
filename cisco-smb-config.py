# This is to generate a base config for a Brocade ICX switch

"""
LIST OF VARIABLES USED
radiusKey
endPort   = last port on switch used for data access like if using 48 port and port 48 is access then end-port is 1/1/47
uplinkPort
nativeVlan
stpPriority   = the priority for the vlans, default is 32768
mgmtIP   = 192.168.70.x mgmt ip
hostname
vlans = a comma separated list of vlans with the format number=name so for example 50=Data
defaultGateway = switches default gateway
deviceType = device_type for netmiko to use
"""


# Read csv is a python file that should exist in the same directory
import csv
from switchconfig import SwitchConfig

class CiscoSMB:

    def __init__(self):
        self.radiusKey = None
        self.endPort = None
        self.uplinkPort = None
        self.nativeVlan = None
        self.stpPriority = 32768
        self.mgmtIP = None
        self.hostname = None
        self.fastOrGig = None
        self.defaultGateway = None
        self.deviceType = None
        self.vlans = {}


    # This will be used to read variables from a csv file
    def readVariables(self, filename="switchcsv.csv"):
        """
        This method will read from a csv and then set the variables accordingly
        :return:
        """
        try:

            # Now we read the values from the csv object
            values = csv.DictReader(open(filename))
            # values is a returned dictionary we iterate through each row
            # The column name at the top determines the key name
            for row in values:
                self.radiusKey = row['radiusKey']
                self.endPort = row['endPort']
                self.uplinkPort = row['uplinkPort']
                self.nativeVlan = row['nativeVlan']
                self.stpPriority = row['stpPriority']
                self.mgmtIP = row['mgmtIP']
                self.hostname = row['hostname']
                self.fastOrGig = row['model']
                self.defaultGateway = row['default-gw']
                self.deviceType = row['device-type']

                # Time to get the vlans, we split on the comma first
                vlanTemp = row['vlans'].split(',')
                # Now loop through that dictionary created
                for vlan in vlanTemp:
                    # This split will make the vlan id in position 0 with the name in position 1
                    # And split on the = sign
                    splitVlanTemp = vlan.split('=')
                    # Add the key as the vlan name and the value as the vlan id
                    self.vlans[splitVlanTemp[1]] = splitVlanTemp[0]

                # Generate the config for that switch
                self.generateConfig()



        except Exception as e:
            # The readCSV file and class will return the error on this one
            print('Failed to open or read from file')
            print(e)





    def generateConfig(self):
        configOutput = """
        conf t
        hostname {hostname}
        errdisable recovery cause all
        errdisable recovery interval 60
        ip dhcp snooping
        ip dhcp snooping verify""".format(hostname=self.hostname)

        for vlanName, vlanID in self.vlans.items():
            # For each vlan, add the config below
            configOutput += """
            vlan {id}
            int vlan {id}
            name {name}
            exit
            ip dhcp snooping vlan {id}
            """.format(id=vlanID, name=vlanName)

        configOutput += """
        int vlan 1
        no ip address dhcp

        ip route 0.0.0.0 0.0.0.0 {defaultGateway}

        username pngadmin privilege 15 password Password123
        enable password Password123
        aaa authentication login default local
        aaa logging login

        line console
        exec-timeout 60

        ip ssh server
        no ip telnet server

        no ip http server
        ip http secure-server
        ip http authentication aaa login-authentication local
        ip http timeout-policy 3600 https-only

        line ssh
        exec-timeout 60

        spanning-tree mode rstp
        spanning-tree priority {stpPriority}

        voice vlan id {voiceVlan}
        Y

        voice vlan state auto-enabled

        management access-list 1
        permit service https
        permit service ssh
        permit service snmp
        management access-class 1

        logging buffered warnings 1000
        logging origin-id hostname

        clock timezone EDT -5
        clock summer-time EDT recurring usa
        clock source sntp

        sntp server time.nist.gov
        sntp unicast client poll
        ip name-server 8.8.8.8

        banner login #
        WARNING:
        This system is provided for business purposes by authorized users
        only.Users of Company resources, including computers, communications
        equipment, and associated services provided by these resources (e.g.,
        Internet, electronic mail, facsimile, voice mail, hardcopy) are to use
        the Company resources for Company business purposes only. The Company
        reserves the right to monitor usage of all resources for auditing purposes
        and whenever deemed necessary by Company. Anyone using this system
        expressly consents to such monitoring. Unauthorized users will be prosecuted
        to the fullest extent of the law.
        #

        interface {uplinkPort}
        description UPLINK
        ip dhcp snooping trust
        no macro auto smartport
        switchport mode trunk
        """.format(uplinkPort=self.uplinkPort, stpPriority=self.stpPriority,
                    nativeVlan=self.nativeVlan, mgmtIP=self.mgmtIP,
                    defaultGateway=self.defaultGateway, voiceVlan=self.vlans['Voice'])

        for vlan in self.vlans.values():
            configOutput += "switchport trunk allowed vlan add {vlanID}\n\t".format(vlanID=vlan)

        configOutput += 'switchport trunk native vlan {nativeVlan}\n'.format(nativeVlan=self.nativeVlan)

        # We have to determine if this is an SF or SG model and go from there
        if self.fastOrGig == "SF":
            configOutput += "\n\tinterface range Fa1 - {endPort}".format(endPort=self.endPort)
        elif self.fastOrGig == "SG":
            configOutput += "\n\tinterface range Gi1 - {endPort}".format(endPort=self.endPort)

        configOutput += """
        switchport mode trunk
        switchport trunk native vlan {dataVlan}
        switchport trunk allowed vlan add {voiceVlan}
        voice vlan enable
        spanning-tree bpduguard enable
        spanning-tree portfast
        port security mode max-addresses
        port security max 10
        port security discard
        no macro auto smartport
        """.format(voiceVlan=self.vlans['Voice'], dataVlan=self.vlans['Data'])

        # Now we connect to the switch IP in the file and apply the config if requested
        applyOrPrint = input("""
        Do you want to apply this config to the switch with ip {ip} or
        just print the output?
        1 = print output
        2 = apply config to {ip}
        """.format(ip=self.mgmtIP))

        # Create an instance of the SwitchConfig class
        sc = SwitchConfig()

        if applyOrPrint == '1':
            print(configOutput)
        elif applyOrPrint == '2':
            username = input('What is the username to use:\n')
            password = sc.getPassword()

            splitConfig = configOutput.splitlines()

            # Call this classes configureSwitch method
            self.configureSwitch(config=splitConfig, username=username, password=password,
                                 ip=self.mgmtIP, deviceType=self.deviceType, scObject=sc)
        else:
            print('Enter a 1 or 2 for this as per the selection screen')


    # This will pass the needed info over the switchconfig module to configure the device
    # We also pass the SwitchConfig object we defined to use its methods
    def configureSwitch(self, config=[], username='none', password='none',
                        ip='none', deviceType='none', scObject='placeholdObject'):

        scObject.connect(ip=ip, device_type=deviceType, username=username, password=password,
                    cmd=config, cmdType='2')








if __name__ == "__main__":

    print('\n\nNOTE: You must first assign the IP address of the switch to the mgmt vlan')
    print('and set up a port to be on the mgmt vlan and enable ssh')
    print('You must also set the system mode to router, this makes it so the script')
    print('Can auto configure the rest of the switch!')
    print('Also another huge note, you must enable ip ssh password-auth for this to work\n')
    print('''
    A little walkthrough of how to do this is by doing:
    1 - in priv exec mode do:
        don't change the password, the script will set it to defaults of pngadmin and Password123
        set system mode router
        accept the reboot, then reconnect
    2 - go into config mode, if vlan 70 is going to be mgmt and switch is 192.168.70.240 then do
        vlan 70
        int vlan 70
        ip add 192.168.70.240 255.255.255.0
    3 - set up a port as the port you will connect to when running the script
        interface gig4
        switchport mode access
        switchport access vlan 70
    4 - enable ssh and turn on ip ssh password-auth so you don't get propmted for username twice!
        ip ssh server
        ip ssh password-auth
    5 - when complete, then run the script
    ''')

    # Make an instance of the class CiscoSMB
    c = CiscoSMB()
    filename = input("What is the filename to use to read from? The default is switchcsv.csv leave blank to use this:\n")
    if filename == "":
        c.readVariables()
    else:
        c.readVariables(filename)







