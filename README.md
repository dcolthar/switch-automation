# switch-automation


The script (brocade-config.py or cisco-smb-config.py) reads from a file named switchcsv.csv by default, you can specify a name when running if you wish.

Column names must be spelled like those in the base-csv.csv file as the scripts look for them

the **uplinkPort** column should the format you would use to enter interface config command in the switch
	-for example in an sf300-24P switch if you use Gig1 as the uplink use Gig1 in the file
	-in an SG300-24P if you use Gig25 enter Gig25
	-in a Brocade ICX switch if you use 1/2/1 then enter that for the value

The **endPort** should be a numerical number representing the final port to apply a base config to
	-for example on an sf300-24p if you only want to apply config across the first 23 ports, use 23
	-In a brocade icx if you only want to apply up to 23 use 23 as well
	
The **nativeVlan** column is the vlan ID that will be used as the untagged/access on the range of ports that are configured
	-This also applies to the uplink port
	
The **mgmtIP** column is the IP to connect to the switch on

The **hostname** column is the hostname to apply to the switch

The **radiusServer** column is the IP/hostname of the radius server to use if applicable

The **radiusKey** column is the secret key to use with the radius server

The **model** column is for cisco SMB switches, specify a SF for SFxxx switches or SG for SGxxx switches

The **vlans** column needs to be formatted as follows
	vlanNumber=Name with a comma between multiple vlan ID's
with no spaces, so for vlan 50 being Data, do 50=Data

**NOTE:** To Determine the Data and Voice VLAN the following is followed:
	The untagged vlan on a port can be named Data or Residents, the script will look for either
	The voice vlan must be named Voice, the script looks for this

The **default-gw** field is the default gateway to use on the switch

The **device-type** section is a device type that netmiko will use for autoconfig
	-for cisco smb use cisco_s300
	-for brocade icx use brocade_fastiron
	-for cisco ios use cisco_ios











