import ctypes
import base64
import json
import time
import argparse
import sys

STOP_AT = 50

# Set default values for domain and cipher
DEFAULT_DOMAIN = 'sample.com'
DEFAULT_CIPHER = 'veryHa7dP4ssW07d'

# Load the shared library
lib = ctypes.CDLL('platforms/macos/arm64/libqbox.dylib')

lib.QBoxStart.argtypes = [ctypes.c_char_p]
lib.QBoxStart.restype = ctypes.c_uint64

lib.QBoxStop.argtypes = [ctypes.c_uint64]
lib.QBoxStop.restype = ctypes.c_int

lib.QBoxVersion.argtypes = []
lib.QBoxVersion.restype = ctypes.POINTER(ctypes.c_char)

lib.QBoxFreeString.argtypes = [ctypes.POINTER(ctypes.c_char)]
lib.QBoxFreeString.restype = None

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Start QBox instance with Base64 encoded config and optional overrides.")
parser.add_argument("-c", "--config", type=str,
                    help="Base64 encoded configuration string")
parser.add_argument("-d", "--domain", type=str, default=DEFAULT_DOMAIN,
                    help="Domain to use in the outbound configuration (default: %(default)s)")
parser.add_argument("-p", "--password", type=str, default=DEFAULT_CIPHER,
                    help="Password/Cipher to use in the outbound configuration (default: %(default)s)")
args = parser.parse_args()

if args.config:
    config_base64 = args.config
else:
    config = {
        "log": {
            "level": "warn",
            "timestamp": True
        },
        "experimental": {
            "cache_file": {
                "enabled": True,
                "store_rdrc": True
            }
        },
        "dns": {
            "servers": [
                {
                    "tag": "remote",
                    "address": "https://1.0.0.1/dns-query",
                    "address_resolver": "local",
                    "client_subnet": "1.0.1.0",
                    "detour": "Proxy"
                },
                {
                    "tag": "local",
                    "address": "udp://119.29.29.29",
                    "detour": "direct-out"
                }
            ],
            "rules": [
                {
                    "outbound": "any",
                    "server": "local",
                    "action": "route"
                },
                {
                    "action": "route-options",
                    "domain": [
                        "*"
                    ],
                    "rewrite_ttl": 64,
                    "udp_connect": False,
                    "udp_disable_domain_unmapping": False
                },
                {
                    "rule_set": "geosite-geolocation-cn",
                    "server": "local",
                    "action": "route"
                },
                {
                    "type": "logical",
                    "mode": "and",
                    "rules": [
                        {
                            "rule_set": "geosite-geolocation-!cn",
                            "invert": True
                        },
                        {
                            "rule_set": "geoip-cn"
                        }
                    ],
                    "server": "remote",
                    "client_subnet": "114.114.114.114/24"
                }
            ],
            "strategy": "ipv4_only",
            "final": "remote",
            "reverse_mapping": True,
            "disable_cache": False,
            "disable_expire": False
        },
        "inbounds": [
            {
                "type": "mixed",
                "tag": "tun-in",
                "listen": "127.0.0.1",
                "listen_port": 1081
            }
        ],
        "outbounds": [
            {
                "tag": "direct-out",
                "type": "direct",
                "udp_fragment": True
            },
            {
                "tag": "Proxy",
                "type": "hysteria2",
                "server": args.domain,
                "server_port": 443,
                "up_mbps": 500,
                "down_mbps": 500,
                "password": args.password,
                "connect_timeout": "5s",
                "tcp_fast_open": True,
                "tls": {
                    "enabled": True,
                    "server_name": args.domain,
                    "alpn": [
                        "h3"
                    ]
                }
            }
        ],
        "route": {
            "final": "Proxy",
            "auto_detect_interface": True,
            "rules": [
                {
                    "inbound": "tun-in",
                    "action": "sniff"
                },
                {
                    "protocol": "dns",
                    "action": "hijack-dns"
                },
                {
                    "rule_set": [
                        "geoip-cn",
                        "geosite-geolocation-cn"
                    ],
                    "outbound": "direct-out"
                },
                {
                    "ip_is_private": True,
                    "outbound": "direct-out"
                },
                {
                    "ip_cidr": [
                        "0.0.0.0/8",
                        "10.0.0.0/8",
                        "127.0.0.0/8",
                        "169.254.0.0/16",
                        "172.16.0.0/12",
                        "192.168.0.0/16",
                        "224.0.0.0/4",
                        "240.0.0.0/4",
                        "52.80.0.0/16"
                    ],
                    "outbound": "direct-out"
                },
                {
                    "rule_set": "geosite-geolocation-!cn",
                    "outbound": "Proxy"
                }
            ],
            "rule_set": [
                {
                    "tag": "geosite-geolocation-cn",
                    "type": "remote",
                    "format": "binary",
                    "url": "https://testingcf.jsdelivr.net/gh/lyc8503/sing-box-rules@rule-set-geosite/geosite-geolocation-cn.srs",
                    "download_detour": "direct-out"
                },
                {
                    "tag": "geosite-geolocation-!cn",
                    "type": "remote",
                    "format": "binary",
                    "url": "https://testingcf.jsdelivr.net/gh/lyc8503/sing-box-rules@rule-set-geosite/geosite-geolocation-!cn.srs",
                    "download_detour": "direct-out"
                },
                {
                    "tag": "geosite-category-ads-all",
                    "type": "remote",
                    "format": "binary",
                    "url": "https://testingcf.jsdelivr.net/gh/lyc8503/sing-box-rules@rule-set-geosite/geosite-category-ads-all.srs",
                    "download_detour": "direct-out"
                },
                {
                    "tag": "geoip-cn",
                    "type": "remote",
                    "format": "binary",
                    "url": "https://testingcf.jsdelivr.net/gh/lyc8503/sing-box-rules@rule-set-geoip/geoip-cn.srs",
                    "download_detour": "direct-out"
                }
            ]
        }
    }
    config_json = json.dumps(config)
    config_base64 = base64.b64encode(config_json.encode()).decode()

version_ptr = lib.QBoxVersion()
if not version_ptr:
    raise RuntimeError("Failed to get version information")

version_cstr = ctypes.string_at(version_ptr).decode("utf-8")
version_json = base64.b64decode(version_cstr)
version_info = json.loads(version_json)

print("Version:", version_info["version"])
lib.QBoxFreeString(version_ptr)

# Start the instance using the provided or default Base64 configuration
instance_id = lib.QBoxStart(config_base64.encode())
if instance_id == 0:
    print("Failed to start instance")
    sys.exit(1)

print(f"Instance started with ID: {instance_id}")
print(f"Running for {STOP_AT} seconds...")
time.sleep(STOP_AT)

result = lib.QBoxStop(instance_id)
if result == 0:
    print("Failed to stop instance")
    sys.exit(1)

print("Instance stopped successfully")
