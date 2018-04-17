# Efergy-SDR

Efergy-SDR uses a cheap RTL-SDR dongle and the power of the [awesome rtl_433 tool](https://github.com/merbanan/rtl_433) to pickup power consumption/generation broadcasts from Efergy energy monitors and pushes this data to PVOutput and/or a Phant server.

After completing this setup, here's how everything will work:

* `capture.py` is started at every boot and in turn starts `rtl_433`
* Any messages output from `rtl_433` matching the specified transmitter ID(s) will be saved in the appropriate `ID_amplog` file for the transmitter.
* Every 5 minutes(or however long you choose), `post.py` will calculate the average, maximum, and minimum values for each of the amplog files, multiply them by the specified voltage in order to get power in Watts, and send them to PVOutput and/or a Phant server. `post.py` then clears the wattlogs.

Designed and tested for Raspberry Pi, however should be very portable, rtl_433 is C and efergy-sdr is Python.

#### A note on Phant
Sparkfun shut down their implementation of Phant (data.sparkfun.com) and ceased development of the Phant platform at the end of 2017. You can still spin up your own Phant server following the directions at [github.com/sparkfun/phant](https://github.com/sparkfun/phant) if you like, however you may need to tweak some things around to get it to run reliably. Or you can just use efergy-sdr to push to PVOutput, which provides ample graphs and analysis for virtually all applications.

If you do decide to use Phant, you will need to create a stream with the fields `average`, `min` and `max`.

* [Install](#install)
* [Setup](#setup)
  * [capture.py](#capturepy)
  * [systemd](#systemd)
  * [screen](#screen)
  * [post.py](#postpy)

## Install
```bash
curl -fsSL https://github.com/Tugzrida/efergy-sdr/raw/master/install.sh | bash
```
(as always ***please*** read the contents of one-liner install scripts before running them as ***they have full access to your entire system***)

## Setup
Connect an RTL-SDR and run `rtl_433 -R 36 -f 433485000`. Take note of the ID reported for the efergy transmitter(s) you wish to use. Pressing the button on the front of the efergy unit briefly to start learning mode will output `Learning: YES` with the transmitter's ID and other details for a few minutes for further identification if there are multiple units within range.

---
### capture.py
Open `~/efergy-sdr/capture.py` and edit the transmitter list at the beginning of the file to specify the ID(s) from the previous step.

You can specify multiple transmitters as follows:
```python
txs = [
    {"id": "123"},
    ...
    {"id": "789"}
]
```
---
### systemd
`capture.py` can be started on boot with systemd. If you don't have systemd or otherwise have objections towards it then you could either use the screen setup below, but if you're technical enough to not like systemd then I'm guessing you won't like screen either, in which case I'm sure you can work it out by yourself :stuck_out_tongue_winking_eye:

Firstly, copy `efergy-sdr.service` to the proper location. Something like this:
```bash
sudo cp /home/pi/efergy-sdr/efergy-sdr.service /etc/systemd/system/
```
(substituting your username if you're not using a Pi)

Then set permissions:
```bash
sudo chown root:root /etc/systemd/system/efergy-sdr.service
sudo chmod 644 /etc/systemd/system/efergy-sdr.service
```

If you're not using a Pi then you'll need to edit `/etc/systemd/system/efergy-sdr.service`(with root permissions) and just change the path of `ExecStart` to point to `capture.py`

The service can then be started up as follows:
```bash
sudo systemctl daemon-reload
sudo systemctl enable efergy-sdr
sudo systemctl start efergy-sdr
```

### screen

**Doing things this way is not great as it won't restart on crash. Use systemd or another service manager if at all possible.**

First install screen with `sudo apt install screen`

Then open `/etc/rc.local` (you'll need root access) and add
```
screen -h 1024 -dmS "efergy-sdr" /home/pi/efergy-sdr/capture.py
```
before the line containing `exit 0`. If you're not running this on a Pi, then you'll need to substitute in your username.

This will start `capture.py` at every boot in a screen session.

---
### post.py
Open `~/efergy-sdr/post.py` and specify the ID(s) just like before. You'll also need to add the AC voltage the transmitter is monitoring. You can also add PVOutput and/or Phant keys to the transmitter entries for data to be logged. (If you don't add any keys, then `post.py` will simply clear the `ID_amplog` files and nothing else, which is pretty boring :( )

```python
txs = [
    {"id": "123", "voltage": 240, "pvo_apikey": "super_secret_numbers", "pvo_sysid": "12345", "pvo_generation": False, "phant_public": "itsasecret", "phant_private": "shhhhhh"},
    ...
    {"id": "456", "voltage": 120, "pvo_apikey": "numbers_numbers_numbers", "pvo_sysid": "67890", "pvo_generation": True, "phant_public": "verysecret", "phant_private": "secretsauce"}
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
