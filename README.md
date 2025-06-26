Juniper VLAN Pruner
===============

-   **Skills:** Python, YML, Markdown, Ansible, Juniper
-   **Source Code Repository:** [Juniper VLAN Pruner](https://github.com/adamrt918/vlan-pruner)
    (Please [email me](https://mail.google.com/mail/u/0/?source=mailto&to=thiemann.adam@gmail.com&su=Github_Access&fs=1&tf=cm) to request access.)

## Project description
This script prunes vlans on the network that are not in use.
This gets the VLANs that are on the user specified core device. Using lldp it crawls through the network, and maps the switch hostname to the vlans on the upstream trunk. Once those VLANs are mapped, it searches the ports downstream to make sure that each vlan is assigned to an interface that is not on an upstream/downstream trunk and is up/up. Any VLANs which are not in use are removed from the interfaces and from the configuration. If there is no interface actively using the VLAN, it will ask if you wish to remove it entirely from your core switch configuration and any trunks throughout the whole network. 

## How to compile and run the program

- Clone the repository onto your ansible server.
- Run 
    > ansible-playbook -i hosts.yml -e "dest=<YOUR_CORE_DEVICE_HOSTNAME>" --diff
- The code will prune VLANs on your network
