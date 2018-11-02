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

* **Barista**: This is the evolution of the coffee button. In addition to the
    big red button it has a few temperature and humidity sensors. Since our
    coffee maker doesn't stop automatically, it is nice to have a way to check
    if it was left on. One of the temperature sensors can be used to monitor the
    temperature of the hot plate of the machine. The other temperature/humidity
    sensor is simply used to give information about the room conditions.
    
    The _barista_ is a **slack bot** meaning that it connects to Slack and monitor
    communications, waiting to be called. It can recognize a few commands such as
    
    * _report_: reports the room conditions
    * _hello_: greet the user
    * _help_: provides information about the commands
    
    In addition, when the button is pressed, it sends a message in the appropriate
    channel to warn everyone that coffee has been brewed!

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
* 1x DHT22 temperature/humidity sensor (for the Barista)
* 1x DS18X20 temperature sensor (for the Barista)
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

For `coffee_button` and `doorman`, get an _incoming-webhook_ URL from your slack account, see the [Slack doc](https://api.slack.com/incoming-webhooks).

For `barista`, you need to create a [Slack bot user](https://api.slack.com/bot-users).

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

For the barista, the configuration is a little bit more advanced

    {
      "wifi" : {
        "SSID" : "my-ssid",
        "pass" : "super-password"
      },
      "slack" : {
        "token" : "<the_slack_token>",
        "bot_token" : "<the_slack_bot_token>",
        "webhook" : "https://hooks.slack.com/services/<long_hex_number>"
      },
      "button" : {
        "channel" : "<slack_channel_id>",
        "message" : "Coffee is ready! :confetti_ball:"
      }
    }

### Make it

1. Solder the sensors and buttons to the ESP32.

    * The push button / reed switch with one leg to ground and the other to
     `pin 22`.
    * The `DHT22` can be connected according to [these instructions](https://learn.adafruit.com/dht/connecting-to-a-dhtxx-sensor)
      with the data leg to `Pin 19`.
    * The `DS18X20` can be connected according to [these instructions](https://learn.adafruit.com/using-ds18b20-temperature-sensor-with-circuitpython/overview) with the data leg to `Pin 21`.

    Summary of connections:
    
        Button/Reed switch <--> 22
        DHT22 <--> 19
        DS18X20 <--> 21

2. Upload the config file and main python scripts

        ampy put coffee_button/config.json
        ampy put coffee_button/main.py
  or

        ampy put doorman/config.json
        ampy put doorman/main.py
  
  or
  
        make barista
        ampy put barista/config.json

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

