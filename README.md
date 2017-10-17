# Efergy-SDR

Efergy-SDR uses a cheap RTL-SDR dongle and the power of the [awesome rtl_433 tool](https://github.com/merbanan/rtl_433) to pickup power consumption/generation broadcasts from Efergy energy monitors and pushes this data to PVOutput and/or Phant(ie. [data.sparkfun.com](https://data.sparkfun.com)).

After completing this setup, here's how everything will work:

* `capture.py` is started at every boot and in turn starts `rtl_433`
* Any messages output from `rtl_433` matching the specified transmitter ID(s) will be saved in the appropriate `ID_amplog` file for the transmitter.
* Every 5 minutes(or however long you choose), `post.py` will calculate the average, maximum, and minimum values for each of the amplog files, multiply them by the specified voltage in order to get power in Watts, and send them to PVOutput and/or Phant. `post.py` then clears the wattlogs.

Designed and tested for Raspberry Pi, however should be very portable, rtl_433 is C and efergy-sdr is Python.

---
## Install
```bash
curl -fsSL https://github.com/Tugzrida/efergy-sdr/raw/master/install.sh | sudo bash
```
(as always ***please*** read the contents of one-liner install scripts before running them-they have full access to your system)

## Setup
Connect an RTL-SDR and run `rtl_433 -R 36 -f 433485000`. Take note of the ID reported for the efergy transmitter(s) you wish to use. Tapping the button on the front of the efergy unit to start learning mode will show `Learning: YES` for a few minutes for further identification if there are multiple units within range.

---
Open `~/efergy-sdr/capture.py` and edit the transmitters list at the beginning of the file to specify the ID(s) from the previous step.

You can specify multiple transmitters as follows:
```python
txs = [
	{"id": "123"},
	...
	{"id": "789"}
]
```

Open `/etc/rc.local` (you'll need root access) and add
```
screen -h 1024 -dmS "efergy-sdr" /home/pi/efergy-sdr/capture.py
```
before the line containing `exit 0`. If you're not running this on a Pi, then you'll need to substitute in your username.

This will start `capture.py` at every boot in a screen session. (yes I know this isn't ideal, but it's very cross-platform and easy :) )

---
Open `~/efergy-sdr/post.py` and specify the ID(s) just like before. You'll also need to add the AC voltage the transmitter is monitoring. You can also add PVOutput and/or Phant (ie. [data.sparkfun.com](https://data.sparkfun.com)) keys to the transmitter entries for data to be logged. (If you don't add any keys, then `post.py` will simply clear the `ID_amplog` files and nothing else, which is pretty boring :( )

```python
txs = [
	{"id": "123", "voltage": 240, "pvo_apikey": "super_secret_numbers", "pvo_sysid": "12345", "pvo_generation": False, "phant_public": "itsasecret", "phant_private": "shhhhhh"},
	...
	{"id": "456", "voltage": 120, "pvo_apikey": "numbers_numbers_numbers", "pvo_sysid": "67890", "pvo_generation": True, "phant_public": "canyoukeepit", "phant_private": "secretsauce"}
]
```

**If you're using PVOutput,** it's important to set `"pvo_generation"` appropriately. Set to `False`, the concerned efergy transmitter will log to **usage** on PVOutput. Setting to `True` will log data from the transmitter as **generation**.

Transmitters set to `True` will also have their output rounded down to 0 if it is less than 20W to prevent logging of night time backdraw of inverters. This value will most likely need tweaking as per your inverter and setup.

Run `crontab -e` and add the following line to the end:
```
*/5 * * * * /home/pi/efergy-sdr/post.py
```
Once again, if you're not running this on a Pi, then you'll need to substitute in your username.

This will run `post.py` every 5 minutes.

---
