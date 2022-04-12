#!/usr/bin/python

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import paho.mqtt.client as mqtt

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Parse ZigBee captures and upload SolarCity data to MQTT')
parser.add_argument('-f', '--filename', type=str, required=True)
parser.add_argument('--mqtt-broker', type=str, required=True)
parser.add_argument('--mqtt-username', type=str, required=True)
parser.add_argument('--mqtt-password', type=str, required=True)
args = parser.parse_args()

def connect_mqtt(args) -> mqtt.Client:
	client = mqtt.Client("solarcity_sniffer")
	client.username_pw_set(args.mqtt_username, args.mqtt_password)

	uri = urlparse(args.mqtt_broker)
	if not uri.scheme:
		pieces = uri.path.split(':')
	else:
		pieces = uri.netloc.split(':')
	default_port = '8883' if uri.scheme == 'mqtts' else '1883'
	(broker, port) = (pieces + [default_port])[0:2]

	if uri.scheme == 'mqtts':
		client.tls_set()
		client.tls_insecure_set(True)

	logging.info(f"Connecting to {broker}:{port} as {args.mqtt_username}")
	client.connect(broker, int(port), keepalive=60, bind_address="")
	client.loop_start()
	return client

mqtt_client = connect_mqtt(args)


def watch_filename(filename):
	last_stats = None
	stats = None

	mtime = lambda stat: None if stat is None else stat.st_mtime
	while True:
		if os.path.exists(filename):
			stats = os.stat(filename)
		if mtime(last_stats) != mtime(stats):
			last_stats = stats
			parse_filename(filename)
		time.sleep(10)

def node_getattr(node, attr):
	if node is not None:
		return node.attrib[attr]

def parse_filename(filename):
	cmd = ['/usr/bin/tshark', '-r', args.filename, '-Y', 'zbee_aps.fragments', '-Tpdml']
	#xml_data = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode("utf-8")
	xml_packets = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout

	registration_data = {}
	report_data = {}
	found_data = False
	for event, elem in ET.iterparse(xml_packets, events=("end",)):
		address = node_getattr(elem.find("proto[@name='zbee_nwk']/field[@name='zbee_nwk.src64']"), 'value')
		if address == None:
			continue
		data = node_getattr(elem.find("proto[@name='fake-field-wrapper']/field[@name='data']"), 'value')
		if data == None:
			continue
		found_data = True
		logging.info("data: " + data)
		if data.startswith('01038a'):
			logging.info('Registration data!')
			registration_data[address] = data
		elif data.startswith('01036800'):
			logging.info('Report data!')
			report_data[address] = data
	if not found_data:
	    logging.info("No data packets found!")

	logging.info("Registration data: " + str(registration_data))
	for address, data in registration_data.items():
		parse_registration(address, data)
	logging.info("Report data: " + str(report_data))
	for address, data in report_data.items():
		parse_report(address, data)

def parse_registration(src_address, data):
	node_id = f"solarcity_{src_address}"
	topic = f"homeassistant/sensor/{node_id}/{node_id}_power/config"

	def decode(b):
		decode = lambda b: bytes.fromhex(b).rstrip(b'\0').decode('utf-8')
		return decode(b)
	brand = decode(data[0x0a*2:0x2b*2])
	model = decode(data[0x2b*2:0x4b*2])
	fw_version = decode(data[0x5b*2:0x5f*2])
	pn = decode(data[0x71*2:0x77*2])
	device_body = dict(
		name = "Solarcity Inverter",
		connections = [["eui64", src_address]],
		manufacturer = brand,
		model = model,
		sw_version = fw_version,
	)
	power_body = dict(
		device = device_body,
		name = "Solarcity Inverter Power",
		unit_of_measurement = "W",
		state_class = "measurement",
		device_class = "power",
		object_id = f"{node_id}_power",
		unique_id = f"{node_id}_power",
		state_topic = f"zigbee/{node_id}/{node_id}_power",
	)
	logging.debug(json.dumps(power_body))
	mqtt_client.publish(topic, json.dumps(power_body), retain=True)

def parse_report(src_address, data):
	node_id = f"solarcity_{src_address}"
	power = int(data[62:66], 16)
	logging.debug(f"Sending power report {power}")
	mqtt_client.publish(f"zigbee/{node_id}/{node_id}_power", power, retain=True)

watch_filename(args.filename)
