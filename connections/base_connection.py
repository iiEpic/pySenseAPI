import json
import os
import requests
import urllib3
from netmiko import ConnectHandler
from .ssh_connection import SSHConnection
from .web_connection import WebConnection

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseConnection:
    def __init__(self, host):
        self.name = host['name']
        self.ip_address = host['ip_address']
        self.username = host['username']
        self.password = host['password']
        self.port = host['port']
        self.connection_method = host['connection_method'].lower()
        self.autoconnect = host['autoconnect']
        self.connection = None

        if self.connection_method == 'web':
            self.base_url = f"https://{self.ip_address}:{self.port}/"
            with open(os.path.join(os.getcwd(), 'endpoints.json'), 'r') as f:
                self.endpoints = json.load(f)
            self.session = requests.session()
            self.session.verify = False
            self.web = WebConnection(self)
        elif self.connection_method == 'ssh':
            self.ssh = SSHConnection(self)

    def _ssh_connect(self):  # Keep this for internal use in ssh_connection.py
        device = {
            "device_type": 'generic',
            "host": self.ip_address,
            "username": os.getenv(self.username),
            "password": os.getenv(self.password),
            "port": self.port
        }
        self.connection = ConnectHandler(**device)

    def _web_get_response(self, url, headers=None):  # Keep for internal use in web_connection.py
        response = self.session.get(url=url, headers=headers)
        return response

    def _web_post_response(self, url, data, headers=None):  # Keep for internal use in web_connection.py
        response = self.session.post(url=url, data=data, headers=headers)
        return response
