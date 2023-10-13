# GoldStar-OS-3000-Waveform-Capture
An experimental script to capture a waveform from a GoldStar OS-3000 Series Oscilloscope


Tested this on my GoldStar OS-3060, worked pretty reliably on 4800 Baud, 9600 Baud worked rarely.

# How to use this

Connect your Oscilloscope to your computer through RS232 as described in the Maunal.
Run `pip3 install -r requirements.txt` and then `python3 main.py <path_to_serial_port> <baud_rate(optional)>`. This will attempt to read the entire waveform from channel 1.
To change the channel, change the `channel`variable on line 77.
