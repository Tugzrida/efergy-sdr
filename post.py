#!/usr/bin/python3

# efergy-sdr: post.py: uploads energy data stored by capture.py to PVOutput and/or Phant
# Copyright (C) 2020 Tugzrida (github.com/Tugzrida)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, time
from requests import get, post

txs = [
    {"id": "123", "voltage": 240, "pvo_apikey": "YOUR_API_KEY", "pvo_sysid": "YOUR_SYSID", "generation": False, "phant_public": "YOUR_PUB_KEY", "phant_private": "YOUR_PRIV_KEY"}
]

for tx in txs:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), 'r') as amplog:
        ampdata = [float(line.rstrip('\n')) for line in amplog]
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), 'w'): pass

    lines = len(ampdata)
    total = sum(ampdata)
    maximum = max(ampdata) * tx["voltage"]
    minimum = min(ampdata) * tx["voltage"]
    average = round((total / lines) * tx["voltage"], 2)

    if tx["generation"]:
        if maximum < 20:
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
        get("http://YOUR_PHANT_SERVER/input/{}?private_key={}&average={}&max={}&min={}".format(tx["phant_public"], tx["phant_private"], average, maximum, minimum))
        print("Posted tx {} to Phant".format(tx["id"]))
    except:
        print("Error posting tx {} to Phant".format(tx["id"]))
