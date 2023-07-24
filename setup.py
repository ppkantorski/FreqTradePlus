from distutils.core import setup
APP = ['app/freqtrade_plus_app.py']
DATA_FILES = [
    'app/freqtrade_plus_app.py',
    'app/icon.icns',
    'app/icon_off.icns',
    'app/icon_stopping.icns'
]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app/icon.icns',
    'plist': {
        'CFBundleShortVersionString': '0.2.0',
        'LSUIElement': True,
    },
    'packages': [],
}
setup(
    app=APP,
    name='FreqTrade+',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['rumps']
)
