import os
import re
from utils import hex_to_dotted_decimal
from datetime import datetime, UTC


class SSHConnection:
    def __init__(self, base_connection):
        self.pfsense = base_connection
        if self.pfsense.autoconnect:
            self.login()

    def login(self):
        self.pfsense._ssh_connect()

    def get_interfaces(self):
        if self.pfsense.connection is None:
            return 'Not connected'
        data = self.pfsense.connection.send_command('ifconfig')

        # Regex patterns
        interface_pattern = re.compile(r"^(\S+): flags")  # Interface name
        description_pattern = re.compile(r"description:\s+(.*?)\s")  # Description
        metric_pattern = re.compile(r"metric (\d+)")  # Metric
        mtu_pattern = re.compile(r"mtu (\d+)")  # MTU size
        inet_pattern = re.compile(r"inet (.*?)\s+netmask\s+(.*?)\s+broadcast\s+(.*?)\s")  # IPv4
        inet6_pattern = re.compile(r"inet6 ([\da-fA-F:]+)")  # IPv6
        groups_pattern = re.compile(r"groups: ([\w\s]+)")  # Groups

        # Splitting each interface block properly
        interfaces = []
        blocks = re.split(r"(?=^\S+: flags)", data, flags=re.MULTILINE)  # Split at interface start

        for block in blocks:
            match_interface = interface_pattern.search(block)
            if match_interface:
                inets = inet_pattern.findall(block)
                for i, inet in enumerate(inets):
                    inets[i] = (inet[0], hex_to_dotted_decimal(inet[1][2:]), inet[2])
                interface = {
                    'name': match_interface.group(1),
                    'description': description_pattern.search(block).group(1) if description_pattern.search(block) else None,
                    'metric': metric_pattern.search(block).group(1) if metric_pattern.search(block) else None,
                    'mtu': mtu_pattern.search(block).group(1) if mtu_pattern.search(block) else None,
                    'inet': inets,
                    'inet6': inet6_pattern.findall(block),
                    'groups': groups_pattern.search(block).group(1).split() if groups_pattern.search(block) else []
                }
                interfaces.append(interface)

        return interfaces

    def get_backup(self, file_path=None):
        print(f'Gathering backup from [{self.pfsense.name}]...')
        if file_path is None:
            if not os.path.exists(self.pfsense.name):
                os.mkdir(self.pfsense.name)
            if not os.path.exists(os.path.join(self.pfsense.name, 'backups')):
                os.mkdir(os.path.join(self.pfsense.name, 'backups'))
            file_path = os.path.join(self.pfsense.name, 'backups',
                                     f'config-{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}.xml')
        data = self.pfsense.connection.send_command('cat /cf/conf/config.xml')
        with open(file_path, 'w+') as f:
            f.writelines(data)
        print('Backed up config.xml to', file_path)

    def disconnect(self):
        if self.pfsense.connection:
            self.pfsense.connection.disconnect()
            self.pfsense.connection = None
