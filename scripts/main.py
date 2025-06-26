#!/usr/bin/env python3
import sys
import pkossh2
import switchVlanMap

output_path = "/etc/ansible/scripts/vlan-pruner/vlan-pruner.txt"

# Start the paramiko connection
pko = pkossh2.SSH()
ssh, shell = pko.connect()
if not ssh:
    sys.exit()

# Create the switch mapping from the core of the respective site.
switch_vlan_map = switchVlanMap.SwitchVlanMap(ssh, shell, pko)
map = switch_vlan_map.get_switch_to_vlan_map()
with open(output_path, 'w') as f:
    f.write(f'{map}')

# Figure out which interfaces are trunked and have VLANs
interfaces = []
switch_to_vlan_dict = {}
append = False

ssh.close()

for switch, allowed_vlans in switch_to_vlan_dict.items():
    ssh, shell = pko.ssh_connect(switch)