# HDIPCAM

A simple python script, with motion detection and recording support for HDIPCAM MEYE-035366-CCFBB camera.

## Introduction

For default use you'll need to create `log`, `storage` and `temp` folders in the directory to which
you clone this repository. This paths can be changed, see parameters bellow.

Python version 3 is required, also make sure you have `Pillow` package...

    # pip install pillow

...and `ffmpeg`, which you can get on their [official website](http://ffmpeg.org/download.html).

To start program in _watchdog_ mode, run: `./hdipcam.py -i <CAM IP AND PORT>`

Common usage example:

    ./hdipcam.py -i 192.168.1.178:9081 -v --user=uname --password=secret --motionat 10 --mask 80.410.230.150,120.0.100.150

## Parameters

### Help

Show help message and exit

    -h, --help

### IP

Camera's IP and port, for example: 192.168.1.1:8020
This parameter is required.

    -i IP, --ip IP

### Verbose

Print detailed information.

    -v, --verbose

### Strikes

_Default: 8_

How many seconds before termination of recording, when no motion detected.
Each strike count as a second. If the value is 5, that mean there will be 5 seconds pause, before recording will be terminated. If in those 5 seconds motion is detected, the timer is reseted.

    -s STRIKES, --strikes STRIKES

### Motionat

_Default: 7_

Level of difference to be considered motion. You can experiment with values in `--test` mode. Usually a good value is between 5 and 15.

    -m MOTIONAT, --motionat MOTIONAT

### Fps

_Default: 2_

Frames per second. Not recommended more than 2.

    -f FPS, --fps FPS

### Pause

_Default: 1_

Pause between two images (when comparing) in seconds. This will capture image A, wait Ns, capture image B, and then compare them.
One to two seconds is usually a good value.

    -p PAUSE, --pause PAUSE

### Mask

Mask to be applied on images when comparing them.

    Format: top.left.width.height,top.left...
    Example: 20.20.200.200,400.400.60.120

This used to ignore motion, if for example your camera is partly capturing a road or a tree which would be swaying in the wind.

    -b MASK, --mask MASK

### Temp

_Default: ./temp_

Temporary folder, where images will be stored for recording and tests.
**WARNING:** content will be deleted. Start with dot for relative.

```
./hdipcam.py --temp ./relative_temp
./hdipcam.py --temp /var/tmp/hdipcam
```
```
--temp TEMP
```

### Storage

_Default: ./storage_

Storage folder for videos.Start with dot for relative.

    --storage STORAGE

### Log

Log file path. If this parameter is absent, logs won't be saved. Start with dot for relative.

    --log LOG

### Uri

_Default: /snapshot.cgi?user=%s&pwd=%s_

Device image URI, with username and password placeholders.

    --uri URI

### User

_Default: None_

Login username, if required.

    --user USER

### Password

Login password if required.

    --password PASSWORD

### Test

Run in test mode, save N of images to storage folder for comparison.

    --test TEST

### Record

Start recording for N seconds.

    --record RECORD

## License

The hdipcam application is licensed under the GPL-3.0 or later.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
