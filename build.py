import os
import shutil
import winsound
import subprocess

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))
    if os.path.exists('./src/res/config'):
        shutil.rmtree('./src/res/config')

    # Get the version of the application
    with open('src/Run.py', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('VERSION = '):
                VERSION = line.split('=')[1].strip().strip("'")
                break

    # Get the list of installed packages and their versions
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
    installed_packages = result.stdout.splitlines()

    packages = {}
    for package in installed_packages:
        packages[package.split('==')[0]] = package.split('==')[1]

    # Read the installer.cfg file
    with open('installer.cfg', 'r') as file:
        lines = file.readlines()

    # Update the versions in the installer.cfg file
    with open('installer.cfg', 'w') as file:
        pypi = False
        section = ""
        for line in lines:
            if line.startswith('['):
                section = line.strip()

            if section == '[Include]' and line.startswith('#[pypi]'):
                pypi = False
            elif section == '[Application]' and line.startswith('version='):
                file.write('version=' + VERSION + '\n')
                continue
            elif pypi:
                p = line.split('==')[0]
                if p.strip() in packages.keys():
                    file.write(p + '==' + packages[p.strip()] + '\n')
                    continue
            elif line.startswith('pypi_wheels ='):
                pypi = True
            file.write(line)

    os.system('pynsist .\\installer.cfg')
    winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
