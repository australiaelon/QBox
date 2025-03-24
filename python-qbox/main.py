import ctypes
import base64
import json
import time
import argparse
import sys

STOP_AT = 50

lib = ctypes.CDLL('platforms/macos/arm64/libqbox.dylib')

lib.QBoxStart.argtypes = [ctypes.c_char_p]
lib.QBoxStart.restype = ctypes.c_uint64

lib.QBoxStop.argtypes = [ctypes.c_uint64]
lib.QBoxStop.restype = ctypes.c_int

lib.QBoxVersion.argtypes = []
lib.QBoxVersion.restype = ctypes.POINTER(ctypes.c_char)

lib.QBoxFreeString.argtypes = [ctypes.POINTER(ctypes.c_char)]
lib.QBoxFreeString.restype = None

parser = argparse.ArgumentParser(description="Start QBox instance with Base64 encoded config.")
parser.add_argument("-c", "--config", type=str, required=True,
                    help="Base64 encoded configuration string")
args = parser.parse_args()

config_base64 = args.config

version_ptr = lib.QBoxVersion()
if not version_ptr:
    raise RuntimeError("Failed to get version information")

version_cstr = ctypes.string_at(version_ptr).decode("utf-8")
version_json = base64.b64decode(version_cstr)
version_info = json.loads(version_json)

print("Version:", version_info["version"])
lib.QBoxFreeString(version_ptr)

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