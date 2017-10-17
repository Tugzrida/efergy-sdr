#!/usr/bin/python
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
