import os
import json
from dotenv import load_dotenv
from pfsenseapi.pfsense import load_hosts

# Load environment variables
load_dotenv()
hosts = load_hosts()


def check_env(args):
    username = os.getenv(args[0])
    password = os.getenv(args[1])
    if username and password:
        print(f"CORE_USERNAME: {username}")
        print("CORE_PASSWORD: Loaded")
    else:
        print("Missing credentials in .env")


def list_hosts():
    print("Loaded Hosts:")
    for host in hosts:
        print(f"- {host.name} ({host.ip_address})")
        try:
            if host.connection:
                print(f"  Version: {host.version}")
                print("  Status: Connected")
            else:
                host.login()
                print(f"  Version: {host.version}")
                print("  Status: Connected")
        except Exception as e:
            print(f"  Status: Connection Failed - {str(e)}")


def list_interfaces(hostname):
    host = [host for host in hosts if host.name.lower() == hostname.lower()] or None
    if host:
        host = host[0]
        print(f"- {host.name} ({host.ip_address})")
        if host.connection is None:
            host.login()
            if host.connection:
                output = host.get_interfaces()
                print(f"  Version: {host.version}")
                print("  Status: Connected")
                print(output)
            else:
                print('  Could not connect to', host.name)
        else:
            output = host.get_interfaces()
            print(f"  Version: {host.version}")
            print("  Status: Connected")
            print(json.dumps(output, indent=2))
    else:
        print('Could not find host with name:', hostname)


def test_connection(hostname):
    host = [host for host in hosts if host.name.lower() == hostname.lower()] or None
    if host:
        host = host[0]
        print(f"- {host.name} ({host.ip_address})")
        if host.connection is None:
            host.login()
            if host.connection:
                print(f"  Version: {host.version}")
                print("  Status: Connected")
            else:
                print('  Could not connect to', host.name)
        else:
            print(f"  Version: {host.version}")
            print("  Status: Connected")
    else:
        print('Could not find host with name:', hostname)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CLI for pySenseAPI")
    parser.add_argument('--check-env', dest='check_env', nargs='+', type=str,
                        help='Username and password variable name you want to check if exists in .env')
    parser.add_argument('--test-connection', type=str,
                        help='Hostname that you wish to test from the hosts.json file')
    parser.add_argument('--list-interfaces', type=str, help='Name of host you wish to get interface status for')
    parser.add_argument('--list-hosts', action='store_true', help='List all loaded hosts and their connection status')
    args = parser.parse_args()

    if args.check_env:
        check_env(args.check_env)

    if args.list_hosts:
        list_hosts()

    if args.list_interfaces:
        list_interfaces(args.list_interfaces)

    if args.test_connection:
        test_connection(args.test_connection)
