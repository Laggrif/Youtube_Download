import os
import shutil
import winsound

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))
    if os.path.exists('./src/res/config'):
        shutil.rmtree('./src/res/config')

    os.system('pynsist .\\installer.cfg')
    winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
