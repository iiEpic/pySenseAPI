from utils import load_hosts
from pfsense import pfSense
from dotenv import load_dotenv

load_dotenv()
hosts = load_hosts()

hosts = [i for i in hosts if i['connection_method'] == 'web']

for host in hosts:
    pfsense = pfSense(host)
    # Get all VLANS as a dict
    # print(pfsense.get_vlans())

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
    #     'tag': '100',
    #     'descr': 'New description for VLAN100',
    #     'vlanif': 'em0.100',
    #     'id': '0',
    #     'save': 'Save'
    # }
    # pfsense.update_vlan(data)

    # Close my connection to pfSense
    pfsense.disconnect()
