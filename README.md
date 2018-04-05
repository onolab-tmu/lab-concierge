Lab Concierge
=============

Lab concierge is a virtual assistant that spreads useful information from the
physical status of our research laboratory to our [Slack](http://www.slack.com)
channel. We use small ESP32 devices with [micropython](https://micropython.org) installed
to monitor useful things.

* **Coffee Button**: We have a large communal coffee pot. A friendly large red
  button stationed next to the pot can be used to inform our lab-mates that
  coffee is ready.

    <img src="https://raw.githubusercontent.com/onolab-tmu/lab-concierge/master/photos/coffee_button.jpg" width="500" align="center">

* **Doorman**: Our lab has only one set of keys that must be obtained from the
  guard at university (a unique security system). Our lab being at the 8th
  floor, if we forget to ask the key, but the lab is still closed, we might
  need to go down. Some extra confusion might happen if meanwhile another
  student come and borrows the key while we are going back down to obtain it.

  This problem is solved by a [reed switch](https://en.wikipedia.org/wiki/Reed_switch)
  that sense the status of the lock on the door. When the status changes,
  it informs the slack channel.

    <img src="https://raw.githubusercontent.com/onolab-tmu/lab-concierge/master/photos/doorman.jpg" width="500" align="center">

We have then a dedicated Slack channel where the information is shared.

<img src="https://raw.githubusercontent.com/onolab-tmu/lab-concierge/master/photos/slack_screen_grab.png" width="500" align="center">

## Replicate it

You will need:

* 1x ESP32 board
* 1x Push button (for the coffee button)
* 1x Reed switch (for the doorman)
* A power supply (I use a USB micro cell phone charger)
* A soldering iron and some wire to connect all the bits together
* A box if you want to make it extra nice

### Preliminaries

#### Micropython

Obtain the latest firmware from
[micropython.org](https://micropython.org/download) and install it with a
variant of the following command.

  esptool.py --chip esp32 --port /dev/ttyUSB1 write_flash -z 0x1000 firmware.bin

Alternatively, use the one in the `firmware/` folder.

#### Get a Slack Hook URL

Get an _incoming-webhook_ URL from your slack account, see the [Slack doc](https://api.slack.com/incoming-webhooks).

#### Install AMPY

Install the `adafruit-ampy` package to upload easily python scripts to the ESP32.

#### Configuration

Modify the JSON configuration file with the wifi SSID and password, as well as
the Slack incoming hook URL previously obtained.

    {
      "wifi" : {
        "SSID" : "my-ssid",
        "pass" : "super-password"
      },
      "slack_hook_url" : "https://hooks.slack.com/services/<long_hex_number>"
    }

### Make it

1. Solder the push button / reed switch with one leg to ground and the other to
   pin 22.

2. Upload the config file and main python scripts

        ampy put coffee_button/config.json
        ampy put coffee_button/main.py
  
  or

        ampy put doorman/config.json
        ampy put doorman/main.py

3. Connect with the power supply and try it out!

## License

    /*
     * ----------------------------------------------------------------------------
     * "THE BEER-WARE LICENSE" (Revision 42):
     * Robin Scheibler wrote this code.  As long as you retain this notice you
     * can do whatever you want with this stuff. If we meet some day, and you think
     * this stuff is worth it, you can buy me a beer in return.   Robin, Gilles, Elie
     * ----------------------------------------------------------------------------
     */

