import re


def get_csrf_token(response):
    try:
        line = [i.strip() for i in response.text.splitlines() if 'var csrfMagicToken' in i.strip()]
        if len(line) != 0:
            line = line[0]
        if matches := re.search(r'var csrfMagicToken\s+=\s+"(.*?)"', line):
            return matches.group(1)
        return None
    except:
        return None


def hex_to_dotted_decimal(hex_string):
    """Converts a hexadecimal string to a dotted decimal string (IPv4 format).

        Args:
            hex_string: The hexadecimal string to convert (e.g., "0A0B0C0D").

        Returns:
            The dotted decimal string (e.g., "10.11.12.13"), or None if the input is invalid.
        """
    if not isinstance(hex_string, str):
        return None

    hex_string = hex_string.lower()
    if not all(c in '0123456789abcdef' for c in hex_string):
        return None

    if len(hex_string) != 8:
        return None

    try:
        decimal_value = int(hex_string, 16)
    except ValueError:
        return None

    octet1 = (decimal_value >> 24) & 255
    octet2 = (decimal_value >> 16) & 255
    octet3 = (decimal_value >> 8) & 255
    octet4 = decimal_value & 255

    return f"{octet1}.{octet2}.{octet3}.{octet4}"
