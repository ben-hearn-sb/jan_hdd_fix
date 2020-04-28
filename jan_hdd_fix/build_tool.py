import PyInstaller.__main__
import os

current_dir = os.path.dirname(__file__)

PyInstaller.__main__.run([
    '--name=%s' % 'jan_hdd_fix',
    '--distpath=%s' % '/Users/benhearn/Documents/jan_hdd_fix/built/dist',
    '--workpath=%s' % '/Users/benhearn/Documents/jan_hdd_fix/built/build',
    '--paths=%s' % '/Users/benhearn/Documents/jan_hdd_fix/ui',
    '--noconfirm',
    '--onefile',
    '--debug=all',
    '--noconsole',
    os.path.join(current_dir + '/main.py')
])