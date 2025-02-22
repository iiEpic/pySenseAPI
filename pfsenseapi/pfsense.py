import html
import json
import os
import re
import requests
import urllib3
from datetime import datetime, UTC
from pfsenseapi.utils import get_csrf_token

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_hosts(filename='hosts.json'):
    """Load hosts from JSON"""
    with open(filename, 'r') as file:
        hosts_data = json.load(file)
    return [pfSense(host) for host in hosts_data]


class pfSense:
    def __init__(self, host):
        self.name = host['name']
        self.ip_address = host['ip_address']
        self.username = host['username']
        self.password = host['password']
        self.port = host['port']
        self.autoconnect = host['autoconnect']
        self.connection = None
        self.base_url = f"https://{self.ip_address}:{self.port}/"
        with open(os.path.join(os.sep, *os.path.abspath(__file__).split('/')[:-1], 'endpoints.json'), 'r') as f:
            self.endpoints = json.load(f)
        self.session = requests.session()
        self.session.verify = False
        self.version = None
        if self.autoconnect:
            self.login()

    def create_vlan(self, data):
        print(f'Creating vlan [{self.name}]...')
        url = self.base_url + self.endpoints.get('edit_vlan')
        response = self._web_get_response(url)
        if response is None:
            print('Failed to get webpage', url)
            return None

        csrf_token = get_csrf_token(response)
        if csrf_token is None:
            print('Could not get CSRF Token', response.text)
            return None

        data['__csrf_magic'] = csrf_token
        response = self._web_post_response(url, data)
        if response is None:
            print('Failed to post to webpage', url)
            return None
        else:
            print(f'Created VLAN {data["tag"]} on {self.name}')

    def delete_vlan(self, data):
        print(f'Deleting vlan [{self.name}]...')
        url = self.base_url + self.endpoints.get('vlan')
        response = self._web_get_response(url)
        if response is None:
            print('Failed to get webpage', url)
            return None

        csrf_token = get_csrf_token(response)
        if csrf_token is None:
            print('Could not get CSRF Token', response.text)
            return None

        data['__csrf_magic'] = csrf_token
        vlan = data['tag']
        data.pop('tag')
        response = self._web_post_response(url, data)
        if response is None:
            print('Failed to post to webpage', url)
            return None
        else:
            print(f'Deleted VLAN {vlan} on {self.name}')

    def disconnect(self):
        response = self._web_get_response(self.base_url + self.endpoints.get('logout'))
        csrf_token = get_csrf_token(response)
        data = {
            'logout': '',
            '__csrf_magic': csrf_token
        }
        self._web_post_response(self.base_url + self.endpoints.get('logout'), data)
        self.connection = None

    def get_backup(self, file_path=None):
        print(f'Gathering backup from [{self.name}]...')
        response = self._web_get_response(self.base_url + self.endpoints.get('backup'))
        if response is None:
            print('Failed to get webpage', self.base_url + self.endpoints.get('backup'))
            return None

        csrf_token = get_csrf_token(response)
        if csrf_token is None:
            print('Could not get CSRF Token', response.text)
            return None

        data = {
            "download": "download",
            "donotbackuprrd": "yes",
            "__csrf_magic": csrf_token
        }
        response = self._web_post_response(self.base_url + self.endpoints.get('backup'), data)

        if response is None:
            print('Failed to get webpage', self.base_url + self.endpoints.get('backup'))
            return None
        else:
            if file_path is None:
                if not os.path.exists(self.name):
                    os.mkdir(self.name)
                if not os.path.exists(os.path.join(self.name, 'backups')):
                    os.mkdir(os.path.join(self.name, 'backups'))
                file_path = os.path.join(self.name, 'backups',
                                         f'config-{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}.xml')
            with open(file_path, "wb") as file:
                file.write(response.content)

            print('Backed up config.xml to', file_path)

    def get_interfaces(self):
        response = self._web_get_response(self.base_url + self.endpoints.get('interface'))
        response_content = response.content.decode()  # Assuming response.content is bytes
        interfaces = self._web_parse_interface_panels(response_content)
        return interfaces

    def get_vlans(self):
        print(f'Getting VLANs on [{self.name}]...')
        url = self.base_url + self.endpoints.get('vlan')
        response = self._web_get_response(url)
        if response is None:
            print('Failed to get webpage', url)
            return None

        pattern = r'(?s)<table class="table.*>(.*?)<\/table>'
        table = re.search(pattern, response.content.decode()).group(0)
        table_headers = re.findall('<th>(.*?)</th>', table)
        table_items = re.findall('(?s)<td>(.*?)</td>', table)

        # Change the last header to ID instead of Actions
        table_headers[-1] = 'ID'

        # Clean up the output
        table_items = [i.strip() for i in table_items]

        # Get the ID of the item
        ids = [re.search(r'id="del-(\d+)">', i).group(1) for i in table_items if re.search('id="(.*?)">', i)]
        vlans = []
        for pos, i in enumerate(range(0, len(table_items), 5)):
            table_item = table_items[i:i + 5]
            table_item[-1] = ids[pos]  # Replace the last item with the ID
            vlan_dict = dict(zip([header.lower().replace(' ', '_') for header in table_headers], table_item))
            vlans.append(vlan_dict)
        return json.dumps(vlans, indent=2)

    def login(self):
        response = self._web_get_response(self.base_url)
        csrf_token = get_csrf_token(response)
        data = {
            'login': 'Login',
            'usernamefld': os.getenv(self.username),
            'passwordfld': os.getenv(self.password),
            '__csrf_magic': csrf_token
        }
        response = self._web_post_response(self.base_url, data)

        if response is None:
            print('Failed to login', self.base_url)
            return None

        response = self._web_get_response(self.base_url)
        version = re.search(r'(?s)<th>Version</th>.*?<td>.*?<strong>(.*?)</strong>', response.content.decode())

        if version:
            self.version = version.group(1)
        self.connection = True

    def update_vlan(self, data):
        print(f'Updating VLAN on [{self.name}]...')
        url = self.base_url + self.endpoints.get('edit_vlan')
        response = self._web_get_response(url, )
        if response is None:
            print('Failed to get webpage', url, {'id': data['id']})
            return None

        csrf_token = get_csrf_token(response)
        if csrf_token is None:
            print('Could not get CSRF Token', response.text)
            return None

        data['__csrf_magic'] = csrf_token
        response = self._web_post_response(url, params={'id': data['id']}, data=data)
        if response is None:
            print('Failed to post to webpage', url)
            return None
        else:
            print(f'Updated VLAN {data["tag"]} on {self.name}')

    def _web_parse_interface_panels(self, response_content):
        # Capture each panel block including its heading and body
        pattern = r'<div class="panel panel-default">(.*?)</div>\s*</div>'
        matches = re.findall(pattern, response_content, re.DOTALL)
        headers = re.findall(r'<dt>(.*?)</dt>', matches[0])

        # Regex patterns
        general_info_pattern = re.compile(r"^(.*?)\s+.*\((.*?),\s+(.*?)\)")

        interfaces = []
        for match in matches:
            interface = {}
            # Extract the heading
            heading_match = re.search(r'<div class="panel-heading">.*?<h2.*?>(.*?)</h2>', match, re.DOTALL)
            heading = heading_match.group(1) if heading_match else None
            interface['display_name'], interface['backend_name'], interface['port'] = general_info_pattern.search(
                heading).groups()

            for header in headers:
                if temp := re.search(
                        re.compile(fr'<dt>{header.replace("(", r"\(").replace(")", r"\)")}.*?<dd>(.*?)\s+<i'), match):
                    interface[header] = re.sub(r'%.*', '', html.unescape(temp.group(1)))
            interfaces.append(interface)

        return interfaces

    def _web_get_response(self, url, headers=None, params=None):  # Keep for internal use in web_connection.py
        if params:
            url += '?'
            for key, value in params.items():
                url += f'&{key}={value}'
        response = self.session.get(url=url, headers=headers)
        return response

    def _web_post_response(self, url, data, headers=None, params=None):  # Keep for internal use in web_connection.py
        if params:
            url += '?'
            for key, value in params.items():
                url += f'&{key}={value}'
        response = self.session.post(url=url, data=data, headers=headers)
        return response
