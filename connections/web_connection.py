import html
import os
import re
from datetime import datetime, UTC
from utils import get_csrf_token


class WebConnection:
    def __init__(self, base_connection):
        self.pfsense = base_connection
        if self.pfsense.autoconnect:
            self.login()

    def login(self):
        response = self.pfsense._web_get_response(self.pfsense.base_url)
        csrf_token = get_csrf_token(response)
        data = {
            'login': 'Login',
            'usernamefld': os.getenv(self.pfsense.username),
            'passwordfld': os.getenv(self.pfsense.password),
            '__csrf_magic': csrf_token
        }
        response = self.pfsense._web_post_response(self.pfsense.base_url, data)

        if response is None:
            print('Failed to login', self.pfsense.base_url)
            return None

    def get_interfaces(self):
        response = self.pfsense._web_get_response(self.pfsense.base_url + self.pfsense.endpoints.get('interface'))
        response_content = response.content.decode()  # Assuming response.content is bytes
        interfaces = self._web_parse_interface_panels(response_content)
        return interfaces

    def get_backup(self, file_path=None):
        print(f'Gathering backup from [{self.pfsense.name}]...')
        response = self.pfsense._web_get_response(self.pfsense.base_url + self.pfsense.endpoints.get('backup'))
        if response is None:
            print('Failed to get webpage', self.pfsense.base_url + self.pfsense.endpoints.get('backup'))
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
        response = self.pfsense._web_post_response(self.pfsense.base_url + self.pfsense.endpoints.get('backup'), data)

        if response is None:
            print('Failed to get webpage', self.pfsense.base_url + self.pfsense.endpoints.get('backup'))
            return None
        else:
            if file_path is None:
                if not os.path.exists(self.pfsense.name):
                    os.mkdir(self.pfsense.name)
                if not os.path.exists(os.path.join(self.pfsense.name, 'backups')):
                    os.mkdir(os.path.join(self.pfsense.name, 'backups'))
                file_path = os.path.join(self.pfsense.name, 'backups',
                                         f'config-{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}.xml')
            with open(file_path, "wb") as file:
                file.write(response.content)

            print('Backed up config.xml to', file_path)

    def disconnect(self):
        response = self.pfsense._web_get_response(self.pfsense.base_url + self.pfsense.endpoints.get('logout'))
        csrf_token = get_csrf_token(response)
        data = {
            'logout': '',
            '__csrf_magic': csrf_token
        }
        self.pfsense._web_post_response(self.pfsense.base_url + self.pfsense.endpoints.get('logout'), data)
        self.pfsense.connection = None

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