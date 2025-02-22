# pySenseAPI

pySenseAPI is a Python library designed to facilitate interaction with pfSense devices through their web interface. It provides an easy-to-use API for managing and retrieving information from pfSense systems.

## Features

- **Simple Interface**: Consistent API for interacting with pfSense devices.
- **Environment Variable Integration**: Securely manage credentials using environment variables.
- **CLI Tool**: Test `.env` credentials and view loaded hosts directly from the command line, among other things.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- `git` installed if you plan to clone it using the CLI commands as show below
- Access to a pfSense device with appropriate credentials

### Installation

Clone the repository:

```bash
git clone https://github.com/iiEpic/pySenseAPI.git
cd pySenseAPI
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

1. **Environment Variables**: Create a `.env` file in the project root directory to store your credentials securely. Use the following format:

   ```env
   CORE_USERNAME=your_username
   CORE_PASSWORD=your_password
   ```

2. **Hosts Configuration**: Define your pfSense hosts in a `hosts.json` file. Example structure:

   ```json
   [
     {
       "name": "pfSense Core",
       "ip_address": "10.0.0.1",
       "username": "CORE_USERNAME",
       "password": "CORE_PASSWORD",
       "port": 443,
       "autoconnect": true
     }
   ]
   ```

### Usage

#### Option one
```python
from pfsenseapi import pfSense

pfsense = pfSense(name="Main pfSense Box", ip_address="10.0.0.1", username="CORE_USERNAME", password="CORE_PASSWORD")
pfsense.login()

print(f"- {pfsense.name} ({pfsense.ip_address})")
   try:
      if pfsense.connection:
          print(f"  Version: {pfsense.version}")
          print("  Status: Connected")
      else:
          pfsense.login()
          print(f"  Version: {pfsense.version}")
          print("  Status: Connected")
   except Exception as e:
      print(f"  Status: Connection Failed - {str(e)}")

pfsense.disconnect()
```

#### Option Two
```python
from pfsenseapi.pfsense import load_hosts
from dotenv import load_dotenv

load_dotenv()
hosts = load_hosts()

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

    # Close my connection to pfSense
    host.disconnect()
```

### Command-Line Interface (CLI)

The CLI tool allows you to test `.env` credentials and view loaded hosts.

To view loaded hosts and their connection status:

```bash
python cli.py --list-hosts
```

To test the credentials stored in your `.env` file and your information in your `hosts.json`:

```bash
python cli.py --test-connection HOSTNAME
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the GNU General Public License v3.0. For more details, refer to the [LICENSE](https://github.com/iiEpic/pySenseAPI/blob/main/LICENSE) file.

