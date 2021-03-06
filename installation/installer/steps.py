import os
import imp
import pip
import shutil
import zipfile
import _winreg
import importlib
import subprocess
import scapy_patch
from colorama import Fore
from utils import create_shortcut, is_64bit_machine, notifier, heights_path, \
    fix_width, DESKTOP_DIR

INSTALLATION_DIR = os.path.join(os.getcwd(), 'installation')
SOFTWARES_DIR = os.path.join(INSTALLATION_DIR, 'softwares')
CACHE_DIRECTORY = os.path.join(INSTALLATION_DIR, 'cache')
SYSTEM_ENVIRON = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'


def uninstall_heights():
    path = heights_path()
    if not path:
        print '[i] Cannot detect old heights installation...'
    else:
        print '[i] Find old heigth installation, trying to uninstall it.'
        print 'Delete Heights Installation:'

        deletes = (
            (shutil.rmtree, 'PortableApps Directory', 'PortableApps'),
            (os.remove, 'Start.exe', 'Start.exe'),
            (os.remove, 'first.bat', 'first.bat'),
            (os.remove, 'first.vbs', 'first.vbs'),
        )

        for func, (msg, file_) in deletes:
            del_path = os.path.join(path, file_)
            if os.path.exists(del_path):
                with notifier(msg, '', True):
                    func(del_path)

        # remove shortcuts
        shortcuts = filter(lambda a: a.endswith('Heights.lnk') or a.endswith(
            'Heights-PyCharm.lnk'),
                           os.listdir(DESKTOP_DIR))
        for shortcut in shortcuts:
            shortcut_path = os.path.join(DESKTOP_DIR, shortcut)
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)

        # remove registry keys
        keys = (
            (_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Classes\Python.File\\'),
            (_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Classes\Pythonw.File\\'),
            (_winreg.HKEY_LOCAL_MACHINE,
             r'SOFTWARE\Classes\wireshark-capture-file\\'),
            (_winreg.HKEY_LOCAL_MACHINE,
             r'SOFTWARE\Wow6432Node\Python\PythonCore\2.7\\'),

            (_winreg.HKEY_CLASSES_ROOT,
             r'Pythonw.File\shell\Open with Heights Pycharm'),
            (_winreg.HKEY_CLASSES_ROOT,
             r'Python.File\shell\Open with Heights Pycharm'),
            (_winreg.HKEY_CLASSES_ROOT,
             r'Pythonw.File\shell\Open with Heights IDLE'),
            (_winreg.HKEY_CLASSES_ROOT,
             r'Python.File\shell\Open with Heights IDLE'),
            (_winreg.HKEY_CLASSES_ROOT,
             r'Pythonw.File\shell\Open with Heights Notepad++'),
            (_winreg.HKEY_CLASSES_ROOT,
             r'Python.File\shell\Open with Heights Notepad++'),
        )
        for key, sub_key in keys:
            _winreg.DeleteKey(key, sub_key)


def install_pycharm():
    installation_path = os.path.join(os.getcwd(), 'pycharm')
    cmd = '{} /S /D={}'.format(os.path.join(SOFTWARES_DIR, 'PyCharm.exe'),
                               installation_path)

    with notifier('PyCharm 2017.1.4'):
        subprocess.call(cmd.split())

    exe_name = 'pycharm'
    if is_64bit_machine():
        exe_name = '{}64'.format(exe_name)
    else:
        print 'Detecting 32bit system...'
        print 'Need to install Java jre...'

        cmd = '{} /s'.format(
            os.path.join(INSTALLATION_DIR, 'jre-8u121-windows-i586.exe'))
        with notifier('Java jre'):
            subprocess.call(cmd.split())

    exe_name = '{}.exe'.format(exe_name)
    exe_path = os.path.join(installation_path, 'bin', exe_name)
    create_shortcut('PyCharm', exe_path)


def install_with_pip(packages_file, notifier_title):
    with open(packages_file) as f:
        for package in f:
            if package.startswith('#'):
                continue
            package = package.strip()
            install_package_with_pip(notifier_title, package)


def install_package_with_pip(notifier_title, package):
    cmd = 'install --find-links={} --no-index -q {}'.format(
        CACHE_DIRECTORY, package)
    with notifier('{} - {}'.format(notifier_title, package)):
        pip.main(cmd.split())


def install_python_packages():
    packages_file = os.path.join(INSTALLATION_DIR, 'python.packages')
    install_with_pip(packages_file, 'Python Package')


def install_networks_packages():
    packages_file = os.path.join(INSTALLATION_DIR, 'networks.packages')
    install_with_pip(packages_file, 'Python Package for Networks')
    scapy_patch.patch()
    install_yore()


def install_winpcap():
    cmd = os.path.join(SOFTWARES_DIR, 'WinPcap.exe')

    with notifier('WinPcap 4.1.3'):
        subprocess.call(cmd.split())


def install_wireshark():
    installation_path = os.path.join(os.getcwd(), 'wireshark')
    zip_path = os.path.join(SOFTWARES_DIR, 'wireshark.zip')

    with notifier('wireshark'), zipfile.ZipFile(zip_path) as f:
        f.extractall(installation_path)

    with notifier('Setting up WIRESHARKPATH environment variable', ''):
        set_system_environment_variable('WIRESHARKPATH', installation_path)

    exe_path = os.path.join(installation_path, 'WiresharkPortable.exe')
    create_shortcut('Wireshark', exe_path)


def set_system_environment_variable(name, value):
    k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, SYSTEM_ENVIRON, 0,
                        _winreg.KEY_WRITE)
    _winreg.SetValueEx(k, name, 0, _winreg.REG_SZ, value)
    _winreg.CloseKey(k)
    return value


def set_environment_variable():
    def read_system_environment_variable(name='path'):
        k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, SYSTEM_ENVIRON)
        value, type_ = _winreg.QueryValueEx(k, name)
        _winreg.CloseKey(k)
        return value

    path = read_system_environment_variable()
    path = path.split(';')

    path = filter(
        lambda a: 'python' not in a.lower() and 'wireshark' not in a.lower(),
        path)

    path.extend(
        [
            os.path.join(os.getcwd(), 'python27'),
            os.path.join(os.getcwd(), 'python27', 'Scripts'),
            os.path.join(os.getcwd(), 'wireshark')
        ]
    )

    set_system_environment_variable('Path', ';'.join(path))


def test_everything_is_good():
    # test for:
    #   [*] python
    #   [*] python libraries
    #   [*] networks libraries
    #   [] pycharm
    #   [] wireshark

    print 'Testing the installation:'
    print '\t[*] {}'.format(
        fix_width('Python install {}successfully'.format(Fore.GREEN)))

    libraries_paths = (
        os.path.join(INSTALLATION_DIR, 'python.packages'),
        os.path.join(INSTALLATION_DIR, 'networks.packages')
    )

    custom_libraries = {
        'ipython': 'IPython',
        'pycrypto': 'Crypto',
        'pyserial': 'serial',
        'python-dateutil': 'dateutil',
        'Pillow': 'PIL'
    }

    for libraries_path in libraries_paths:
        with open(libraries_path) as file_:
            for library in file_:
                if library.startswith('#'):
                    continue

                library = library.strip().split('=')[0]
                library = custom_libraries.get(library, library)
                try:
                    importlib.import_module(library)
                    msg = '{}successfully'.format(Fore.GREEN)
                except ImportError:
                    msg = '{}failed'.format(Fore.RED)

                print '\t[*] Python package - {:15} import {}'.format(library,
                                                                      msg)

    print '{}YAY everything is install! have fun'.format(Fore.LIGHTRED_EX)
    raw_input('Press any key to continue...')


def install_yore():
    install_package_with_pip('Install yore-socket', os.path.join(CACHE_DIRECTORY, 'yore-socket.zip'))

    with notifier('Installing yore change into scapy'):
        print ''
        path = os.path.join(INSTALLATION_DIR, 'get-scapy-yore.py')
        get_scapy_yore = imp.load_source('get_scapy_yore', path)
        get_scapy_yore.main(True)


if __name__ == '__main__':
    install_yore()
