import os
import shutil

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    os.system('.\\venv\\Scripts\\pyinstaller '
              '--noconfirm '
              '--onedir '
              '--windowed '
              '--icon "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/res/icon/download.ico" '
              '--name "Youtube Download" '
              '--clean '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/config.py;." '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/Directory.py;." '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/MainWindow.py;." '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/res/style.qss;res/" '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/utils.py;." '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/Youtube_music_downloader.py;." '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/YTDL.py;." '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/ffmpeg;ffmpeg/" '
              '--add-data "C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/res/icon;res/icon" '
              '"C:/Users/Laggrif/Documents/Coding_Projects/Youtube Download/src/Run.py"')
    if os.path.exists('./dist/Youtube Download/_internal/res/config'):
        shutil.rmtree('./dist/Youtube Download/_internal/res/config')
    shutil.copy('src/vc.exe', './dist/Youtube Download')
