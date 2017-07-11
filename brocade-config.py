# This is to generate a base config for a Brocade ICX switch

"""
LIST OF VARIABLES USED
radiusKey
endPort =  last port on switch used for data access like if using 48 port and port 48 is access then end-port is 1/1/47
uplinkPort
nativeVlan
stpPriority   = the priority for the vlans, default is 32768
mgmtIP   = 192.168.70.x mgmt ip
hostname
vlans = a comma separated list of vlans with the format number=name so for example 50=Data
defaultGateway = switches default gateway
deviceType = device_type for netmiko to use
radiusServer = radius server IP address
"""


# Read csv is a python file that should exist in the same directory
import csv
from switchconfig import SwitchConfig


class Brocade:

    def __init__(self):
        self.radiusKey = None
        self.radiusServer = None
        self.endPort = None
        self.uplinkPort = None
        self.nativeVlan = None
        self.stpPriority = 32768
        self.mgmtIP = None
        self.hostname = None
        self.defaultGateway = None
        self.deviceType = None
        self.vlans = {}


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
                self.radiusServer = row['radiusServer']
                self.endPort = row['endPort']
                self.uplinkPort = row['uplinkPort']
                self.nativeVlan = row['nativeVlan']
                self.stpPriority = row['stpPriority']
                self.mgmtIP = row['mgmtIP']
                self.hostname = row['hostname']
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
        configure terminal
        clock summer-time
        clock timezone us Eastern

        ntp
        server 24.56.178.140

        no telnet server

        console timeout 60
        ip ssh timeout 60

        radius-server host {radiusServer} auth-port 1812 acct-port 1813 default key {radiusKey}

        enable aaa console
        aaa authentication web-server default local radius
        aaa authentication login default local radius
        aaa authentication login privilege-mode
        aaa accounting system default start-stop radius



        no web-management http
        web-management https
        web-management session-timeout 3600

        errdisable recovery cause all
        errdisable recovery interval 60""".format(radiusKey=self.radiusKey, radiusServer=self.radiusServer)



        for vlanName, vlanID in self.vlans.items():
        # For each vlan, add the config below
            configOutput += """
            vlan {id} name {name}
            tagged ethernet 1/1/1 to 1/1/{endPort}
            tagged ethernet {uplinkPort}
            spanning-tree 802-1w
            spanning-tree 802-1w priority {stpPriority}
            ip dhcp snooping vlan {id}
            """.format(id=vlanID, name=vlanName, stpPriority=self.stpPriority,
                                                 uplinkPort=self.uplinkPort, endPort=self.endPort)
        configOutput += """
        no ip proxy-arp
        no ip source-route
        no ip directed-broadcast
        logging buffered warnings
        optical-monitor

        fdp run
        cdp run
        lldp run
        lldp med network-policy application voice tagged vlan {voiceVlan} priority 5 dscp 46 port eth1/1/1 to 1/1/{endPort}

        banner motd %
        WARNING:^C
        This system is provided for business purposes by authorized users
        only.Users of Company resources, including computers, communications
        equipment, and associated services provided by these resources (e.g.,
        Internet, electronic mail, facsimile, voice mail, hardcopy) are to use
        the Company resources for Company business purposes only. The Company
        reserves the right to monitor usage of all resources for auditing purposes
        and whenever deemed necessary by Company. Anyone using this system
        expressly consents to such monitoring. Unauthorized users will be prosecuted
        to the fullest extent of the law.
        %

        Ip route 0.0.0.0 0.0.0.0 {defaultGateway}

        Interface ethernet {uplinkPort}
        Port-name Uplink
        dhcp snooping trust
        spanning-tree 802-1w admin-pt2pt-mac
        Dual-mode {nativeVlan}

        Interface ethernet 1/1/1 to 1/1/{endPort}
        Dual-mode {nativeVlan}
        Voice-vlan {voiceVlan}
        spanning-tree 802-1w admin-edge-port
        stp-bpdu-guard
        Port security
        violation restrict
        Maximum 10
        inline power power-limit 15400

        Hostname {hostname}""".format(voiceVlan=self.vlans['Voice'], nativeVlan=self.nativeVlan,
                                        uplinkPort=self.uplinkPort, endPort=self.endPort,
                                      hostname=self.hostname, defaultGateway=self.defaultGateway)

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
    b = Brocade()
    sc = SwitchConfig()

    # Print off the preconfig steps that need to be done
    print("""
pre-config script and steps that need to be run on each switch prior to applying config with this script:

1 - Please verify the device is running Router code, 7250 will need to be booted into secondary flash
2 - Prior to doing the reboot if changing to router code, run the following command and write memory
enable
configure terminal
enable acl-per-port-per-vlan
wr mem

3 - If the unit was not running router code in the primary image slot after reboot, copy router code
    to the primary flash spot as well using the following command in privileged exec mode:
copy flash flash primary

4 - you will then need to set a username/password, an IP address for management and enable SSH
    some example commands to do this say using vlan 70 as management with ip of 192.168.70.240
    and also assing the mgmt vlan to a port so the device can access the switch to run the tool:
configure terminal
username [enter username] priv 0 password [enter password]
enable super-user-password [enter enable password]
aaa authentication login default local
aaa authentication login privilege-mode

crypto key generate rsa modulus 2048
crypto-ssl certificate generate
vlan 70 name Mgmt
spanning-tree 802-1w
router-interface ve 70
untagged ethernet 1/1/24

interface ve 70
ip add 192.168.70.240 255.255.255.0

5 - When this is complete on all devices in scope continue with the script
    """)


    filename = input("What is the filename to use to read from? The default is switchcsv.csv leave blank to use this:\n")
    if filename == "":
        b.readVariables()
    else:
        print('you entered a filename of {filename}'.format(filename=filename))
        b.readVariables(filename)

    # After each switch is done just run this to let the user know

    sc.printSpacer()
    print("""
    Some commands to run after install, if you do so before the switch
    can contact Radius you will get slowdown on commands:

        aaa accounting commands 0 default start-stop radius
    """)
    sc.printSpacer()




