# CHAMP_Battlebox
This is the Raspberry Pi 4, and Arduino interface for our battlebox.

### Touch Screen Configuration/Setup

We expect the touch screen to be attached to the pi 4 in the HDMI 1 position.

Make sure to configure the touch screen so it attaches to the first monitor.
`crontab -l` will display the crontab for the current user pi.

We added `@reboot xinput map-to-output 6 HDMI-1` to the file in order to correctly identify
and add the touch interface to the touch screen monitor.


### Setting up the arduino

The following instructions were used to set up the pi to talk the the arduino.
https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/

We are expecting to connect throught the USB port.

`sudo adduser your_username dialout`

needed to install a special driver for the arduino nano that was being used:
This was used to get communication working via windows at first:
https://sparks.gogo.co.nz/ch340.html

The arduino nano worked under linux when selecting the ATmega328 version of the nano from boards
in the arduino IDE.
