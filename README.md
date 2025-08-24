# Basic app to download music from youtube

## Installation
Download the .exe file from the <a href='https://github.com/Laggrif/Youtube_Download/releases/latest'>release page</a> and proceed with the installer.

## Building
Clone the project on your local machine, download ffmpeg from <a href='https://ffmpeg.org/download.html'>their website</a> and extract it under ```src/ffmpeg```.
To build the installer, you will need to install NSIS. You can find it on <a href='https://nsis.sourceforge.io/Download'>their website</a>.
Install the python packages with ```pip install requirements.txt``` and run ```Build.py```. You now have your own .exe installer

## Still in development, new features will eventually be added
Do not hesitate to ask for features and make suggestions or pull requests.

### Please Help

I am ultimately planning on putting a protection so you cannot download unsupported urls. 
For the time, it is only a manually written blacklist. Therefore, if you see any youtube url that is not working (for example `https://www.youtube.com`), please put a response to <a href='https://github.com/Laggrif/Youtube_Download/issues/1'>this issue</a> with the url and I will add them to the blacklist as soon as possible.

## Dependencies
This project make use of <a href='https://github.com/yt-dlp/yt-dlp'>yt-dlp</a> and <a href='https://wiki.qt.io/Qt_for_Python'>Pyside6</a>. A huge thanks to them for their amazing work.

<br>
<br>
<br>

### Donate

If you love my work and want to support me, feel free to buy me a coffee (or more) with the button below

[![Paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/donate/?hosted_button_id=QU79XQ3CGUP74)
