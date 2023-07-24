import os, sys
import shutil

# check min. python version
if sys.version_info < (3, 8):  # pragma: no cover
    sys.exit("Freqtrade+ requires Python version >= 3.8")

# Install module if not already installed
import importlib
def install(package):
    try:
        importlib.import_module(package)
    except ImportError:
        os.system(f"pip3 install {package}")

# Import / Install
packages = ['py2app', 'rumps']
[install(pkg) for pkg in packages]

# Define script path
script_path = os.path.dirname(os.path.abspath( __file__ ))

os.system(f"rm -rf {script_path}/FreqTrade+.app")

# Run setup script
os.system(f'python3 {script_path}/setup.py py2app -A')

# Clean up directories
shutil.rmtree(f'{script_path}/build')
os.system(f'mv {script_path}/dist/FreqTrade+.app {script_path}/FreqTrade+.app')
shutil.rmtree(f'{script_path}/dist')

# Build helpers scripts
os.system(f"rm -rf {script_path}/helpers/date_prompt.app")
os.system(f"osacompile -o {script_path}/helpers/date_prompt.app {script_path}/helpers/date_prompt.scpt")
os.system(f"defaults write '{script_path}/helpers/date_prompt.app/Contents/Info.plist' LSUIElement -bool yes")
os.system(f'yes | cp {script_path}/app/icon.icns {script_path}/helpers/date_prompt.app/Contents/Resources/applet.icns')
