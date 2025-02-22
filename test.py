from pfsenseapi.pfsense import load_hosts
from dotenv import load_dotenv

load_dotenv()
hosts = load_hosts()

for host in hosts:
    # Get all VLANS as a dict
    # print(host.get_vlans())

    # Create a new VLAN
    # data = {
    #     'if': 'em0',
    #     'tag': '999',
    #     'descr': 'testing',
    #     'save': 'Save'
    # }
    # pfsense.create_vlan(data)

    # Delete an existing VLAN
    # data = {
    #     'tag': '999',
    #     'act': 'del',
    #     'id': 4
    # }
    # pfsense.delete_vlan(data)

    # Update an existing VLAN
    # data = {
    #     'if': 'em0',
    #     'tag': '2',
    #     'descr': 'VLAN2',
    #     'vlanif': 'em0.2',
    #     'id': '2',
    #     'save': 'Save'
    # }
    # pfsense.update_vlan(data)

    # Close my connection to pfSense
    host.disconnect()
