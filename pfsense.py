from connections.base_connection import BaseConnection


class pfSense(BaseConnection):
    def __init__(self, host):
        super().__init__(host)
        self.interface = self.web if self.connection_method == 'web' else self.ssh

    def connect(self):
        self.interface.login()

    def get_backup(self):
        return self.interface.get_backup()

    def get_interfaces(self):
        return self.interface.get_interfaces()

    def disconnect(self):
        self.interface.disconnect()
