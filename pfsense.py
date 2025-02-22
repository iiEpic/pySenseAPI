from connections.base_connection import BaseConnection


class pfSense(BaseConnection):
    def __init__(self, host):
        super().__init__(host)
        self.interface = self.web if self.connection_method == 'web' else self.ssh

    def create_vlan(self, data):
        # data should be a dict
        self.interface.create_vlan(data)

    def connect(self):
        self.interface.login()

    def delete_vlan(self, data):
        # data should be a dict
        self.interface.delete_vlan(data)

    def disconnect(self):
        self.interface.disconnect()

    def get_backup(self):
        return self.interface.get_backup()

    def get_interfaces(self):
        return self.interface.get_interfaces()

    def get_vlans(self):
        return self.interface.get_vlans()

    def update_vlan(self, data):
        return self.interface.update_vlan(data)
