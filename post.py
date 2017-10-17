#!/usr/bin/python
import os, time
from requests import get, post

txs = [
	{"id": "123", "voltage": 240, "pvo_apikey": "YOUR_API_KEY", "pvo_sysid": "YOUR_SYSID", "pvo_generation": False, "phant_public": "YOUR_PUB_KEY", "phant_private": "YOUR_PRIV_KEY"}
]

for tx in txs:
	amplog = [float(line.rstrip('\n')) for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), 'r')]
	open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), 'w').close()
	
	lines = len(amplog)
	total = sum(amplog)
	maximum = max(amplog) * tx["voltage"]
	minimum = min(amplog) * tx["voltage"]
	average = round((total / lines) * tx["voltage"], 2)
		
	if tx["pvo_generation"]:
		if average < 20:
			maximum = minimum = average = 0
		pvodata = {'c1': '1', 'data': "{},,{}".format(time.strftime("%Y%m%d,%H:%M"), average)}
	else:
		pvodata = {'c1': '1', 'data': "{},,,,{}".format(time.strftime("%Y%m%d,%H:%M"), average)}
	
	try:
		post("https://pvoutput.org/service/r2/addbatchstatus.jsp", data=pvodata, headers={'X-Pvoutput-Apikey': tx["pvo_apikey"], 'X-Pvoutput-SystemId': tx["pvo_sysid"]})
		print("Posted tx {} to PVOutput".format(tx["id"]))	
	except:
		print("Error posting tx {} to PVOutput".format(tx["id"]))

	try:
		get("http://data.sparkfun.com/input/{}?private_key={}&average={}&max={}&min={}".format(tx["phant_public"], tx["phant_private"], average, maximum, minimum))
		print("Posted tx {} to Phant".format(tx["id"]))	
	except:
		print("Error posting tx {} to Phant".format(tx["id"]))
