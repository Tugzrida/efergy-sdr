# Efergy-SDR

Efergy-SDR uses a cheap RTL-SDR dongle and the power of the [awesome rtl_433 tool](https://github.com/merbanan/rtl_433) to pickup power consumption/generation broadcasts from Efergy energy monitors and pushes this data to PVOutput and/or a Phant server.

After completing this setup, here's how everything will work:

* `capture.py` is started at every boot and in turn starts `rtl_433`
* The current value(Amps) of any messages recieved by `rtl_433` matching the specified transmitter ID(s) will be saved in a file named `ID_amplog`.
* Every 5 minutes, `post.py` will calculate the average, maximum, and minimum values for each of the `ID_amplog` files, multiply them by the specified voltage in order to get power in Watts, and send the average to PVOutput and/or the average, max and min to a Phant server. `post.py` then clears the amp logs.

Efergy-SDR was designed and tested for Raspberry Pi, however it should be very portable - rtl_433 is C and Efergy-SDR is Python.

#### A note on Phant
Sparkfun shut down their implementation of Phant (data.sparkfun.com) and ceased development of the Phant platform at the end of 2017. You can still spin up your own Phant server following the directions at [github.com/sparkfun/phant](https://github.com/sparkfun/phant) if you like, however you may need to tweak some things around to get it to run reliably (have a look at the archived issues for some pointers). Or you can just use efergy-sdr to push to PVOutput, which provides ample graphs and analysis for virtually all applications.

If you do decide to use Phant, you will need to create a stream with the fields `average`, `min` and `max`.

* [Install](#install)
* [Setup](#setup)
  * [capture.py](#capturepy)
  * [Auto start](#auto-start)
    * [systemd](#systemd)
    * [screen](#screen)
  * [post.py](#postpy)

## Install
```bash
curl -fsSL https://github.com/Tugzrida/efergy-sdr/raw/master/install.sh > /tmp/efergy-sdr-install;
echo "9cc1b9a06a2362e2a14deb93f96d931a8a2d28eb  /tmp/efergy-sdr-install" | sha1sum -c - && bash /tmp/efergy-sdr-install;
```
(as always ***please*** read the contents of one-liner install scripts before running them as ***they have full access to your entire system***)

## Setup
Connect an RTL-SDR and run `rtl_433 -R 36 -f 433485000`. Take note of the ID reported for the efergy transmitter(s) you wish to use. If you want to log more than one transmitter, or there is more than one within range, pressing the button on the front of the efergy unit briefly to start learning mode will show `Learning: YES` in packets received from that transmitter for a few minutes.

---
### capture.py
Open `~/efergy-sdr/capture.py` and edit the transmitter list at the beginning of the file to specify the ID(s) from the previous step.

You can specify multiple transmitters as follows:
```python
txs = {
    "123": {"name": "House usage"},
    "456": {"name": "1.68kW solar"},
    ...
    "789": {"name": "12.16kW solar"}
}
```

The `name` field is only used for [IFTTT](https://ifttt.com) low battery notificaions, which can be optionally setup as follows:

1. Create an applet on IFTTT with a webhook called `notify` as "this" and a notification with body `{{Value1}}` as "that".
2. Take your webhooks key from [https://ifttt.com/maker_webhooks](https://ifttt.com/maker_webhooks)`> Documentation` and insert it into `capture.py` in place of `YOUR_KEY` near the end of the script.

---
### Auto start
#### systemd
`capture.py` can be started on boot with systemd. If you don't have systemd then you could use the [screen setup](#screen) below, but it's not ideal.

Firstly, copy `efergy-sdr.service` to the proper location. Something like this:
```bash
sudo cp ~/efergy-sdr/efergy-sdr.service /etc/systemd/system/
```

Then set permissions:
```bash
sudo chown root:root /etc/systemd/system/efergy-sdr.service
sudo chmod 644 /etc/systemd/system/efergy-sdr.service
```

If you're not using a Pi then you'll need to edit `/etc/systemd/system/efergy-sdr.service`(with root privileges) and just change the path of `ExecStart` to point to `capture.py` where this repo is cloned.

The service can then be enabled to run on boot as follows:
```bash
sudo systemctl daemon-reload
sudo systemctl enable efergy-sdr
```

And finally started with:
```bash
sudo systemctl start efergy-sdr
```

#### screen

**Doing things this way is not great as it won't restart on crash. Use systemd or another service manager if at all possible.**

First install screen with `sudo apt install screen`

Then open `/etc/rc.local` (you'll need root access) and add
```
screen -h 1024 -dmS "efergy-sdr" /home/pi/efergy-sdr/capture.py
```
before the line containing `exit 0`. You'll need to substitute in your username to make the path point to `capture.py` where this repo is cloned.

This will start `capture.py` at every boot in a screen session.

---
### post.py
Open `~/efergy-sdr/post.py` and specify the ID(s) similar to before. You'll also need to add the AC voltage the transmitter is monitoring. You can also add PVOutput and/or Phant keys to the transmitter entries for data to be logged. (If you don't add any keys, then `post.py` will simply clear the `ID_amplog` files and nothing else, which is pretty boring :( )

```python
txs = [
    {"id": "123", "voltage": 240, "pvo_apikey": "super_secret_numbers", "pvo_sysid": "12345", "generation": False, "phant_public": "itsasecret", "phant_private": "shhhhhh"},
    {"id": "456", "voltage": 240, "pvo_apikey": "very_secret_numbers", "pvo_sysid": "67890", "generation": False, "phant_public": "donttellanyone", "phant_private": "my_dogs_name"},
    ...
    {"id": "789", "voltage": 120, "pvo_apikey": "numbers_numbers_numbers", "pvo_sysid": "54321", "generation": True, "phant_public": "verysecret", "phant_private": "secretsauce"}
]
```

**It's important to set `"generation"` correctly.** Set to `False`, the concerned efergy transmitter will log to **usage** on PVOutput. Setting to `True` will log data from the transmitter as **generation**.

Transmitters with `"generation"` set to `True` will also have their outputs rounded down to 0 when their maximum value over 5 minutes is less than 20 Watts. This is to prevent the logging of night time back-draw of inverters. This value will most likely need tweaking as per your inverter and setup.

Run `crontab -e` and add the following line to the end:
```
*/5 * * * * /home/pi/efergy-sdr/post.py
```
Once again, you'll need to substitute in your username to make the path point to `capture.py` where this repo is cloned.

This will run `post.py` every 5 minutes.
