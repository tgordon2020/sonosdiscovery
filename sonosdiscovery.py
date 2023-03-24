import socket
import requests
import xmltodict
import csv

upnp_msg = \
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST:239.255.255.250:1900\r\n' \
    'ST:upnp:rootdevice\r\n' \
    'MX:2\r\n' \
    'MAN:"ssdp:discover"\r\n' \
    '\r\n'

upnp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
upnp_send.settimeout(2)
upnp_send.sendto(upnp_msg.encode('utf-8'), ('239.255.255.250', 1900))

sonos_list = []
sonos_data = []

device_num = 0

try:
    while True:
        data, addr = upnp_send.recvfrom(65507)
        if "Sonos" in data.decode():
            for line in data.decode().split("\r\n"):
                if "SECURE" in line:
                    pass
                elif "LOCATION:" in line:
                    sonos_list.append(line.split(": ")[1])
                    device_num = device_num + 1
                    print(f"Found {device_num} sonos device(s)")
                else:
                    pass
        else:
            pass
except socket.timeout:
    pass

for sonos_dev in sonos_list:
    sonos_dict = {}
    sonos_resp = requests.get(sonos_dev)
    doc = xmltodict.parse(sonos_resp.text)
    for k,v in doc['root']['device'].items():
        if isinstance(v,str):
            sonos_dict[k]=v
        else:
            pass
    sonos_data.append(sonos_dict)

fieldnames = set(list(k for y in sonos_data for k,v in y.items()))

with open("Sonos.csv", "w", newline='') as sonos_writer:
    writer = csv.DictWriter(sonos_writer,fieldnames=fieldnames)
    writer.writeheader()
    for s in sonos_data:
        writer.writerow(s)
