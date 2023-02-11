import os
import shutil

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    os.system('.\\venvAnaconda\\Scripts\\pyinstaller.exe '
              '--noconfirm '
              '--onedir '
              '--windowed '
              '--icon "J:/Coding_Projects/Youtube Download/res/icon/download.ico" '
              '--name "Youtube Download" '
              '--add-data "J:/Coding_Projects/Youtube Download/config.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/Directory.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/MainWindow.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/Run.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/Test.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/utils.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/Youtube_music_downloader.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/YTDL.py;." '
              '--add-data "J:/Coding_Projects/Youtube Download/res;res/" '
              '--add-data "J:/Coding_Projects/Youtube Download/ffmpeg;ffmpeg/" '
              '--add-data "J:/Coding_Projects/Youtube Download/README.md;." '
              '--add-data "J:/Coding_Projects/Youtube Download/style.qss;."  '
              '"J:/Coding_Projects/Youtube Download/Run.py"')
    if os.path.exists('./dist/Youtube Download/res/config'):
        shutil.rmtree('./dist/Youtube Download/res/config')
    shutil.copy('./vc.exe', './dist/Youtube Download')
