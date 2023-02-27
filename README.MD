# Bundles everything in an Anaconda environment and creates an installer.

## Tested with Anaconda3, Python 3.9.16, Windows 10

## All your py-files and any other file you want to add to your app need to be in the ROOT of your env.

### pip install env2installer

### Please install:

#### pyinstaller

pip install -U pyinstaller 

#### ImageMagick (for the icon)

[https://imagemagick.org/script/download.php](https://imagemagick.org/script/download.php)

#### Inno Setup (to create the installer)

[https://jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)  

```python
from env2installer import create_installer_exe

# the file for the icon, size doesn't matter
image_for_icon = r"C:\Users\Gamer\Videos\bilder2\2021-02-06 03_49_36-Window.png"

# there will be 2 output folders: c:\proxytyri_temp and c:\proxytyri
# the setup-up file will be: "C:\proxytyri\proxyfilesdownl_setup.exe"
outputfolder = "c:\\proxytyri"

# your py file, make sure that it is in the root of your env!
pyfile = r"C:\Users\Gamer\anaconda3\envs\royalehigh\downloadproxies.py"

# name of you app
appname = "proxyfilesdownl"

# your name
autor = "arni"

# path of ImageMagick 
magickpath = r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"

create_installer_exe(
    image_for_icon,
    outputfolder,
    pyfile,
    appname,
    autor,
    version="1", # version as string
    LicenseFile=None, # If None, an empty file will be added. The license file will be shown to the user during the installation.
    InfoBeforeFile=None,  # If None, an empty file will be added. The file will be shown to the user during the installation.
    InfoAfterFile=None, # If None, an empty file will be added. The file will be shown to the user during the installation.
    url="https://127.0.0.1", # your url
    innosetupfilepath=r"C:\Program Files (x86)\Inno Setup 6\Compil32.exe", # the Inno Setup executable
    magickpath=magickpath, # path of ImageMagick 
    excludepackages=("pip",), # packages you want to exclude 
    add_to_pyinstaller_cmd=''  # commands to add to pyinstaller, like "--noconsole"
)
```
