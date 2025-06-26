import jsonDepth
import json




class SwitchVlanMap():
    def __init__(self, connection, shell, pko):
        self.ssh = connection
        self.shell = shell
        self.pko = pko
        self.interfaces = []
        self.vlan_switch_map = {}
        self.json_depth = jsonDepth.jsonDepth()

    def get_switch_to_vlan_map(self):
        # Extract JSON output from LLDP command
        lldp_output = self.pko.send_command(self.shell, "show lldp neighbors | display json | no-more")

        # Create the json depth object and modify the output into valid JSON
        lldp_output = self.json_depth.get_depth(lldp_output)
        lldp_dict = json.loads(lldp_output)
        lldp_dict = lldp_dict['lldp-neighbors-information']
        lldp_dict = lldp_dict[0]['lldp-neighbor-information']
        for intf in lldp_dict:

            # Get the lists of ports
            parent_list = intf.get('lldp-local-parent-interface-name', [])
            local_list = intf.get('lldp-local-port-id', [])
            remote_system_name = intf.get('lldp-remote-system-name', [])

            # Only get the self.interfaces which connect to network gear
            if len(remote_system_name) > 0 and remote_system_name[0]['data'].startswith('sw-'):

                # Only add non-null values
                # Only add if not already in the interfaces list
                if (
                    parent_list 
                    and parent_list[0]['data'] != '-'
                    and parent_list[0]['data'] not in self.interfaces
                ):
                    self.interfaces.append(parent_list[0]['data'])
                    append = True
                else:

                    # fallback: use local port (not in a LAG)
                    # ensure the local list exists, is not already in the list
                    # and is not null
                    if (
                        local_list 
                        and local_list[0]['data'] not in self.interfaces 
                        and local_list[0]['data'] != '-'
                        and parent_list[0]['data'] not in self.interfaces
                    ):
                        self.interfaces.append(local_list[0]['data'])
                        append = True

            # Get the vlans on the appended interface
            if append:
                intf_vlans = self.pko.send_command(
                    self.shell, 
                    f"show configuration interfaces {self.interfaces[len(self.interfaces) - 1]} | display json | no-more"
                )
                intf_vlans = self.json_depth.get_depth(intf_vlans)
                intf_vlans = json.loads(intf_vlans)
                intf_vlans = intf_vlans['configuration']['interfaces']['interface'][0]['unit'][0]
                intf_vlans = intf_vlans['family']['ethernet-switching']['vlan']['members']

                # Add to dict with a key that is the hostname of the remote system and the values are the list of vlans.
                self.vlan_switch_map[remote_system_name[0]['data']] = set()
                self.vlan_switch_map[remote_system_name[0]['data']].update(intf_vlans)

            append = False

            # Map the vlans to their respective IDs
            vlan_id_map = self.get_vlan_id()

            # Put VLAN IDs only in the switch map (get rid of vlan names)
            self.vlan_switch_map = self.standardize_vlans(vlan_id_map, self.vlan_switch_map)

        return self.vlan_switch_map
    
    #This function maps the vlan names to their respective IDs.
    def get_vlan_id(self):

        # Get VLAN configuration output from the switch and modify to a valid json format
        command = 'show configuration vlans | display json | no-more'
        vlan_output = self.pko.send_command(self.shell, command)
        vlan_output = self.json_depth.get_depth(vlan_output)
        vlan_list = json.loads(vlan_output)
        vlan_list = vlan_list['configuration']['vlans']['vlan']

        # Create the dictionary of vlans
        vlan_id_map = {}
        for vlan in vlan_list:
            vlan_id_map[vlan['name']] = set()
            vlan_id_map[vlan['name']] = vlan['vlan-id']
        return vlan_id_map

    # This function takes the vlan to id map and switch to vlan map 
    # and normalizes all of the names.
    def standardize_vlans(self, vlan_id_map, vlan_switch_map):
        normalized = {}
        # Iterate through the switch to vlan map -- through each key
        for switch, vlans in vlan_switch_map.items():
            normalized_vlans = []

            # Iterate through the vlans in each key
            for vlan in vlans:

                # If it's already an integer, or a numeric string, keep as-is
                if isinstance(vlan, int):
                    normalized_vlans.append(vlan)
                elif vlan.isdigit():
                    normalized_vlans.append(int(vlan))

                # If it's a known VLAN name, replace with ID
                elif vlan in vlan_id_map:
                    normalized_vlans.append(vlan_id_map[vlan])
                else:
                    print(f"Warning: unknown VLAN '{vlan}' on {switch}")
            
            # write to the new dict once every vlan key is added.
            normalized[switch] = normalized_vlans
        return normalized
                
