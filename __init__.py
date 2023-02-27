import re
import subprocess
import sys
import tempfile
import uuid

from PIL import Image
from flexible_partial import FlexiblePartialOwnName
from touchtouch import touch
import os

sysp = os.path.normpath(os.sep.join(sys.executable.split(os.sep)[:-1]))


def get_all_non_py_files_in_root():
    return [
        os.path.normpath(os.path.join(sysp, x))
        for x in os.listdir(sysp)
        if not str(x).lower().endswith(".py")
        and not os.path.isdir(os.path.join(sysp, x))
    ]


def get_all_package_imports(exclude):
    packagepath = os.path.normpath(os.path.join(sysp, r"Lib\site-packages"))
    allpa = list(set([x.split("-")[0].split(".")[0] for x in os.listdir(packagepath)]))
    goodpa = []
    for pa in allpa:

        try:
            if "pyinstaller" in pa.lower() or "_pycache" in pa.lower() or pa in exclude:
                continue
            exec(f"import {pa}")
            print(f"Adding: {pa}")
            goodpa.append(pa)
        except Exception as fe:
            continue
    x1 = [f"--hidden-import {x}" for x in goodpa]
    x2 = [f"--collect-submodules {x}" for x in goodpa]
    x3 = [f"--collect-data {x}" for x in goodpa]
    x4 = [f"--collect-binaries {x}" for x in goodpa]
    x5 = [f"--collect-all {x}" for x in goodpa]
    # x6= [
    #     f"--copy-metadata {x}"
    #     for x in goodpa
    # ]
    allto = []
    allto.extend(x1)
    allto.extend(x2)
    #
    allto.extend(x3)
    allto.extend(x4)
    allto.extend(x5)
    # allto.extend(x6)
    allimportscommandstr = " ".join(allto)
    return allimportscommandstr


def get_folder_file_complete_path(folders):
    if isinstance(folders, str):
        folders = [folders]
    listOfFiles2 = []
    for dirName in folders:
        for (dirpath, dirnames, filenames) in os.walk(dirName):
            listOfFiles2.extend(
                list(os.path.normpath(os.path.join(dirpath, d)) for d in dirnames)
            )
    fin = [x for x in list(set(listOfFiles2)) if os.path.isdir(x)]
    addi = [
        r"C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs",
        r"C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x86",
        r"C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64",
        r"C:\Program Files (x86)\Windows Kits\11\Redist\ucrt\DLLs",
        r"C:\Program Files (x86)\Windows Kits\11\Redist\ucrt\DLLs\x86",
        r"C:\Program Files (x86)\Windows Kits\11\Redist\ucrt\DLLs\x64",
    ]
    fin.extend(addi)
    return fin


def add_binary_to_files(nonpyfiles):
    nonpyfilesto = [
        f'--add-binary "{x}";.'
        for x in nonpyfiles
        if not str(x).lower().endswith("exe") and not str(x).lower().endswith("dll")
    ]
    return " ".join(nonpyfilesto)


def create_icon(imagepath, fo, magickpath="magick"):
    nameiconfile = os.path.normpath(os.path.join(fo, "appicon_color.ico"))
    nameiconfile_bw = os.path.normpath(os.path.join(fo, "appicon_bw.ico"))

    write_icon_file(imagepath, nameiconfile, nameiconfile_bw, magickpath=magickpath)
    return nameiconfile, nameiconfile_bw


def get_path_of_others(fo):
    fox = get_folder_file_complete_path(folders=fo)  # [100:200]
    paths = " ".join(
        [
            f'--paths "{x}"'
            for x in fox  # "-" not in x
            # and " " not in x
            # and "'" not in x
            if '"' not in x
            and "pyinstal" not in x
            and "." not in x
            and "\\.idea" not in x
            and "\\__pycache__" not in x
            and "\\conda-meta" not in x
            and "\\DLLs" not in x
            and "\\etc" not in x
            and "\\include" not in x
            and "\\Lib" not in x
            and "\\Library" not in x
            and "\\libs" not in x
            and "\\Scripts" not in x
            and "\\share" not in x
            and "\\Tools" not in x
        ]
    )
    return paths


def get_distpath_vars(dispath):

    dispath = os.path.normpath(dispath)
    distemp = dispath + "_temp"
    if not os.path.exists(dispath):
        os.makedirs(dispath)
    if not os.path.exists(distemp):
        os.makedirs(distemp)

    dispath = f" --distpath {dispath} "
    distemp = f" --workpath {distemp} "
    return dispath, distemp


def create_installer(
    imageforicon,
    outputfolder,
    mainfile,
    appname,
    exclude,
    add_to_cmd="",
):

    allimportscommandstr = get_all_package_imports(exclude)
    nonpyfiles = get_all_non_py_files_in_root()
    adddata = add_binary_to_files(nonpyfiles)
    fo = os.path.normpath("\\".join(sys.executable.split("\\")[:-1]))

    nameiconfile = imageforicon
    name = appname
    envname = sys.executable.split(os.sep)[-2]

    mainfile = os.path.normpath(mainfile)
    paths = get_path_of_others(fo)
    dispath, distemp = get_distpath_vars(dispath=outputfolder)
    whoco = rf"pyinstaller {add_to_cmd} --noconfirm --onedir{dispath}{distemp}--icon {nameiconfile} --name {name} --clean {adddata} {paths} {allimportscommandstr} {mainfile}"

    fosc = os.path.join(fo, "Scripts")
    batchfile = os.path.join(fosc, "makeinstaller.bat")
    batchfile2 = os.path.join(fosc, "exemakeinstaller.bat")
    hdd = fo[:2]
    with open(batchfile2, mode="w", encoding="utf-8") as f:
        f.write(
            f"""{hdd}\ncd\\\ncd {fo}\ncd Scripts\nCALL activate {envname}\nCALL {batchfile}\n"""
        )
    with open(batchfile, mode="w", encoding="utf-8") as f:
        f.write(f"""{whoco}\n""")

    subprocess.run(batchfile2, shell=True)
    try:
        os.remove(batchfile2)
    except Exception:
        pass
    try:
        os.remove(batchfile)
    except Exception:
        pass


def write_icon_file(imagepath, nameiconfile, nameiconfile_bw, magickpath="magick"):
    magick_convert_command = f'"{magickpath}" convert'

    icon = Image.open(imagepath)
    allpictures = {}
    different_sizes = [16, 32, 128, 256, 512]
    for size in different_sizes:
        pic = icon.resize((size, size))
        allpictures[f"{size}x{size}_temppic.png"] = pic.copy()

    for path, pic in allpictures.items():
        pic.save(path)
        magick_convert_command = magick_convert_command + f" {path}"

    magick_convert_command = magick_convert_command + f" {nameiconfile}"
    os.system(magick_convert_command)

    for path, pic in allpictures.items():
        pic = pic.convert("L").convert("RGB")
        pic.save(path)
        magick_convert_command = magick_convert_command + f" {path}"

    magick_convert_command = magick_convert_command + f" {nameiconfile_bw}"
    os.system(magick_convert_command)

    for path, pic in allpictures.items():
        try:
            os.remove(path)
        except Exception as Fehler:
            print(Fehler)
    print(magick_convert_command)
    return imagepath, nameiconfile, nameiconfile_bw


def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles += getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return [os.path.normpath(x) for x in allFiles]


def write_setup_file(
    path,
    appname,
    iconpfad,
    LicenseFile,
    InfoBeforeFile,
    InfoAfterFile,
    name_of_exe,
    version,
    url,
    autor,
    outputfolder,
):
    setupfile = re.sub(r"\.exe$", "_setup", name_of_exe.lower())

    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)

    alledateien = getListOfFiles(path)
    alledateien.sort(reverse=True)
    alleanhaengen = []
    for albundy in alledateien:
        if not albundy:
            continue
        if os.path.isdir(albundy):
            continue
        aktualisiert = albundy.replace(path + "\\", "")
        wievielebackslashes = aktualisiert.count("\\")
        if wievielebackslashes == 0:
            alleanhaengen.append(
                rf"""Source: "{albundy}"; DestDir: "{{app}}"; Flags: ignoreversion"""
            )
            continue
        elif wievielebackslashes > 0:
            mitsubfolder = re.sub(r"\\[^\\]+$", "", aktualisiert)
            alleanhaengen.append(
                rf"""Source: "{albundy}"; DestDir: "{{app}}\{mitsubfolder}"; Flags: ignoreversion"""
            )
    allefiles = "\n" + "\n".join(alleanhaengen).strip() + "\n"

    header = rf'''#define MyAppName "{appname}"
#define MyAppVersion "{version}"
#define MyAppPublisher "{autor}"
#define MyAppURL "{url}"
#define MyAppExeName "{name_of_exe}"'''

    setup = rf"""[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{{{{uuid.uuid1()}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
;AppVerName={{#MyAppName}} {{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=no
LicenseFile={LicenseFile}
InfoBeforeFile={InfoBeforeFile}
InfoAfterFile={InfoAfterFile}
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={outputfolder}
OutputBaseFilename={setupfile}
SetupIconFile={iconpfad}
Compression=lzma
SolidCompression=yes
WizardStyle=modern"""

    andereconfigs = r"""[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "armenian"; MessagesFile: "compiler:Languages\Armenian.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "bulgarian"; MessagesFile: "compiler:Languages\Bulgarian.isl"
Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
Name: "corsican"; MessagesFile: "compiler:Languages\Corsican.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
Name: "icelandic"; MessagesFile: "compiler:Languages\Icelandic.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "slovak"; MessagesFile: "compiler:Languages\Slovak.isl"
Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]"""

    iconsrun = rf"""[Icons]
Name: "{{group}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"
Name: "{{group}}\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\{{#MyAppName}}"; Filename: "{{app}}\{{#MyAppExeName}}"; Tasks: desktopicon


[Run]
Filename: "{{app}}\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram}},{{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent"""

    komplettekonfig = (
        header
        + "\n\n"
        + setup
        + "\n\n"
        + andereconfigs
        + "\n"
        + allefiles
        + "\n"
        + iconsrun
    )
    komplettekonfig = komplettekonfig.strip()
    komplettekonfig = komplettekonfig.strip()
    setup_file = os.path.normpath(os.path.join(path, "innosetup.iss"))
    with open(setup_file, mode="w", encoding="utf-8") as f:
        f.write(komplettekonfig)
    return setup_file


def _get_remove_file(file):
    return FlexiblePartialOwnName(os.remove, f"os.remove({repr(file)})", True, file)


def get_tmpfile(suffix=".bin"):
    tfp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    filename = tfp.name
    filename = os.path.normpath(filename)
    tfp.close()
    touch(filename)
    return filename, _get_remove_file(filename)


def create_installer_exe(
    image_for_icon,
    outputfolder,
    pyfile,
    appname,
    autor,
    version="1",
    LicenseFile=None,
    InfoBeforeFile=None,
    InfoAfterFile=None,
    url="https://127.0.0.1",
    innosetupfilepath=r"C:\Program Files (x86)\Inno Setup 6\Compil32.exe",
    magickpath="magick",
    excludepackages=(),add_to_pyinstaller_cmd=''
):

    image_for_icon = os.path.normpath(image_for_icon)
    outputfolder = os.path.normpath(outputfolder)
    pyfile = os.path.normpath(pyfile)
    version = str(version)
    if not LicenseFile:
        LicenseFile, LicenseFile_remove_file = get_tmpfile(suffix=".txt")
    if not InfoBeforeFile:
        InfoBeforeFile, InfoBeforeFile_remove_file = get_tmpfile(suffix=".txt")
    if not InfoAfterFile:
        InfoAfterFile, InfoAfterFile_remove_file = get_tmpfile(suffix=".txt")

    nameiconfile, nameiconfile_bw = create_icon(
        imagepath=image_for_icon, fo=sysp, magickpath=magickpath
    )

    create_installer(
        imageforicon=nameiconfile,
        outputfolder=outputfolder,
        mainfile=pyfile,
        exclude=excludepackages,
        appname=appname, add_to_cmd=add_to_pyinstaller_cmd.strip()
    )

    setup_file = write_setup_file(
        path=os.path.normpath(os.path.join(outputfolder, appname)),
        appname=appname,
        iconpfad=nameiconfile,
        LicenseFile=LicenseFile,
        InfoBeforeFile=InfoBeforeFile,
        InfoAfterFile=InfoAfterFile,
        name_of_exe=appname + ".exe",
        version=version,
        url=url,
        autor=autor,
        outputfolder=outputfolder,
    )

    subprocess.run(f'''\"{innosetupfilepath}\" /cc "{setup_file}"''')
    return setup_file

