#!/usr/bin/python

# efergy-sdr: capture.py: saves data transmitted by efergy wireless current transducers
#                         and stores it for upload to PVOutput and/or Phant by post.py
# Copyright (C) 2018 Tugzrida (github.com/Tugzrida)
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

import subprocess, os
from json import loads
from requests import post

txs = [
    {"id": "123", "name": "House usage"}
]

for tx in txs:
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), 'w').close()
    tx["batteryLowSent"] = False

rtl433 = subprocess.Popen(["/usr/local/bin/rtl_433", "-R36", "-f433485000", "-q", "-Fjson"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

for line in iter(rtl433.stdout.readline, b''):
    try:
        rcvdJson = loads(line)
        for tx in txs:
            if str(rcvdJson["id"]) == tx["id"]:
                amplog = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), "a")
                amplog.write("{}\n".format(str(rcvdJson["current"])))
                amplog.close()
                if rcvdJson["battery"] == "LOW":
                    print("{} transmitter battery is low".format(tx["name"]))
                    if tx["batteryLowSent"] == False:
                        try:
                            post("https://maker.ifttt.com/trigger/notify/with/key/YOUR_KEY", data={"value1": "{} Efergy transmitter battery is low".format(tx["name"])})
                            tx["batteryLowSent"] = True
                        except:
                            print("Error sending battery alert")
                else:
                    tx["batteryLowSent"] = False
    except ValueError:
        pass
