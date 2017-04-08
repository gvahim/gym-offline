import os
import string
import platform
import subprocess
from ctypes import windll
from colorama import Fore
from contextlib import contextmanager

SHORTCUT = INSTALLATION_DIR = os.path.join(os.getcwd(), 'installation', 'Shortcut.exe')
DESKTOP_DIR = os.path.join(os.path.expanduser('~'), 'Desktop')


def create_shortcut(shortcut_name, path):
    msg = '[i] Creating shortcut for {}'.format(shortcut_name)
    print fix_width(msg),
    cmd = '{} /A:C /F:{}\\{}.lnk /T:{}'.format(SHORTCUT, DESKTOP_DIR, shortcut_name, path)
    with open(os.devnull, 'w') as fnull:
        subprocess.call(cmd.split(), stdout=fnull)
    print '{}[D O N E]'.format(Fore.LIGHTMAGENTA_EX)


def is_valid_os():
    """
    :return: if os version is windows 7 and above
    :rtype: bool
    """
    raise NotImplementedError()


def is_64bit_machine():
    """    
    :return: return true if the machine is 64bit otherwise return false.
    :rtype: bool
    """
    return platform.machine().endswith('64')


@contextmanager
def install_notifier(name):
    msg = '[i] installing {}...'.format(name)
    print fix_width(msg),
    yield
    print '{}[D O N E]'.format(Fore.LIGHTMAGENTA_EX)


def get_drives():
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            yield letter
        bitmask >>= 1


def fix_width(msg, width=65):
    fmt = '{{:{}}}'.format(width)
    return fmt.format(msg)


def heights_path():
    for drive in get_drives():
        dirs = filter(lambda a: 'heights' == a.lower(), os.listdir('{}:\\'.format(drive)))
        if len(dirs) == 1:
            return r'{}:\{}'.format(drive, dirs[0])
    return None

if __name__ == '__main__':
    print SHORTCUT
    create_shortcut('ori', 'c:\python27\python.exe')
    print list(get_drives())
    print heights_path()
