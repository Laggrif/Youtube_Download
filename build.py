import os
import shutil

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    os.system('.\\venvAnaconda\\Scripts\\pyinstaller '
              '--noconfirm '
              '--onedir '
              '--windowed '
              '--icon "J:/Coding_Projects/Youtube Download/res/icon/download.ico" '
              '--name "Youtube Download" '
              '--clean '
              '--add-data "J:/Coding_Projects/Youtube Download/src/config.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/Directory.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/MainWindow.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/style.qss;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/utils.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/Youtube_music_downloader.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/YTDL.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/src/ffmpeg;ffmpeg/" '
              '--add-data "J:/Coding_Projects/Youtube Download/res/icon;res/icon" '
              '--add-data "J:/Coding_Projects/Youtube Download/src/vc.exe;." '
              '"J:/Coding_Projects/Youtube Download/src/Run.py"')
    if os.path.exists('./dist/Youtube Download/res/config'):
        shutil.rmtree('./dist/Youtube Download/res/config')
    shutil.copy('src/vc.exe', './dist/Youtube Download')
