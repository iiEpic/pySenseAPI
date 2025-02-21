from utils import load_hosts
from pfsense import pfSense
from dotenv import load_dotenv

load_dotenv()
hosts = load_hosts()

for host in hosts:
    pfsense = pfSense(host)
    pfsense.get_backup()
    pfsense.disconnect()
