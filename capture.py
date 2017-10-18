#!/usr/bin/python

# efergy-sdr: capture.py: saves data transmitted by efergy wireless current transducers
#                         and stores it for upload to PVOutput and/or Phant by post.py
# Copyright (C) 2017 Tugzrida (github.com/Tugzrida)
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

import subprocess, re, os

txs = [
    {"id": "123"}
]

for tx in txs:
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), 'w').close()

rtl433 = subprocess.Popen(["/usr/local/bin/rtl_433", "-R", "36", "-f", "433485000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

for line in iter(rtl433.stdout.readline, b''):
    for tx in txs:
        if "Transmitter ID:	 {}".format(tx["id"]) in line:
            amps = float(re.search('[0-9]*\.[0-9][0-9]', rtl433.stdout.readline()).group(0))
            amplog = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}_amplog'.format(tx["id"])), "a")
            amplog.write("{0}\n".format(amps))
            amplog.close()
