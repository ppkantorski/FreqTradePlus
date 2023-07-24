__author__ = "b0rd2dEAth"
__version__ = "1.0.2"
__maintainer__ = "b0rd2dEAth"
__status__ = "Development Build"

import rumps
from AppKit import NSAttributedString
from PyObjCTools.Conversion import propertyListFromPythonCollection
from Cocoa import (NSFont, NSFontAttributeName, NSColor, NSForegroundColorAttributeName)
import os, sys
import shutil
import importlib
import datetime as dt
import time
import webbrowser
import threading
import json
import ast
from pprint import pprint
import applescript
import validators
#import freqtrade

# check min. python version
if sys.version_info < (3, 8):  # pragma: no cover
    sys.exit("Freqtrade+ requires Python version >= 3.8")

sys.dont_write_bytecode = True
app_path = os.path.dirname(os.path.abspath( __file__ ))
helpers_path = app_path.replace('/app', '/helpers')
servers_path = app_path.replace('/app', '/servers')
logs_path = app_path.replace('/app', '/logs')


# FreqTrade Imports
######################################################
import logging
from typing import Any, List
from freqtrade.commands import Arguments
from freqtrade.exceptions import FreqtradeException, OperationalException
from freqtrade.loggers import setup_logging_pre
######################################################





#freqtrade_path = "/Users/ppkantorski/freqtrade/freqtrade"
#sys.path.append(freqtrade_path)
#import main


# Define user's executables
SSHFS_EXEC = "/opt/homebrew/bin/sshfs"
#FREQTRADE_EXEC = "/Users/ppkantorski/miniforge3/envs/py10/bin/freqtrade"
#FREQTRADE_EXEC = "/Users/ppkantorski/miniforge3/bin/freqtrade"
FREQTRADE_EXEC = "python3 /Users/ppkantorski/freqtrade/freqtrade/main.py"
SERVER_USER = "ubuntu"
SERVER_DIR = f"/home/{SERVER_USER}"
#sys.path.insert(0, '/Users/ppkantorski/freqtrade')

# FreqTradePlus Class Object
class FreqTradePlusApp(object):
    def __init__(self):
        # Initialize FreqTrade
        #self.retro_sync = FreqTrade()
        #self.retro_sync.verbose = False
        
        # Overload the FreqTrade notify function
        #self.retro_sync.notify = self.notify
        
        #self.app_cfg = DEFAULT_RETROSYNC_CFG
        #self.reload_config()
        
        # Initialize Process queue dict
        self.queue = {}
        
        # Initialize bot menu list
        self.bot_menu = []
        
        if os.path.exists(f'{app_path}/app_config.json'):
            try:
                with open(f'{app_path}/app_config.json', 'r') as f:
                    self.app_config = json.load(f)
                    #self.bot_labels = self.app_config['bot_labels']
                    self.bot_count = len(self.app_config['bot_labels'])
                    for bot_label in self.app_config['bot_labels']:
                        if bot_label not in self.app_config.keys():
                            self.app_config[bot_label] = {}
                self.write_app_config()
                
                failed_load = False
            except:
                failed_load = True
        
        if not (os.path.exists(f'{app_path}/app_config.json')) or failed_load:
            self.app_config = {
                'bot_labels': []
            }
            self.bot_count = 0
            self.write_app_config()
        
        
        
        
        self.menu_labels = {
            "app_name": "FreqTrade+",
            "add_bot": "\uFF0B Add New Bot",
            "about": "About FreqTrade+ \uD83E\uDD16",
            "restart": "Restart",
            "quit": "Quit",
        }
        
        self.bot_menu_labels = {
            "start": "\u25B6 Start",
            "stop": "\u25A0 Stop",
            "auto_start_off": "    Auto-Start",
            "auto_start_on": "\u2713 Auto-Start",
            "download": "Download...",
            "download_data": "Download Data",
            "download_all_data": "Download All Data",
            "open": "Open...",
            "open_freq_ui": "Open FreqUI",#\uD83D\uDD17
            "open_config": "Open Config",
            "open_script": "Open Script",
            "open_location": "Open in Finder",
            "backtest": "Backtest...",
            "options": "Options...",
            "run_backtest": "Run Backtest",
            "plot": "Plot...",
            "plot_dataframes": "Plot DataFrame(s)",
            "plot_profit": "Plot Profit",
            "configure": "Configure...",
            "set_server_type": "Set Server Type",
            "enable_remote_server": "Enable Remote Server",
            "disable_remote_server": "Disable Remote Server",
            "set_location": "Set User Data",
            "set_strategy": "Set Strategy",
            "set_pairs": "Set Pair(s)",
            "set_start_date": "Set Start Date",
            "set_end_date": "Set End Date",
            "set_timeframe": "Set Timeframe",
            "set_timeframes": "Set Timeframe(s)",
            "enable_alternate_stakes": "Enable Alternate Stakes",
            "disable_alternate_stakes": "Disable Alternate Stakes",
            "rename": "Rename Bot",
            "remove_bot": "Remove Bot",#\u2212 
            "server": "Server...",
            "mount_server": "\u23FB Mount Server",
            "unmount_server": "\u23CF Unmount Server",
            "set_server_ip": "Set Server IP",
            "set_server_key": "Set Server Key",
        }
        
        self.options = {
            "auto_start": False,
        }
        
        self.app = rumps.App(self.menu_labels["app_name"], quit_button=None)
        
        # Initialize RSID
        self.obstruct = Obstruct()
        self.obstruct.seed = int((random.getnode()**.5+69)*420)
        self.password_prompt()
        
        # Initialize menu
        #self.stop_loop.stop()
        #self.stop_loop.count = 0
        self.app.title = ''
        self.app.icon = f'{app_path}/icon_off.icns'
        
        # Read Options file (used for storing app specific options like auto start)
        if os.path.exists(f'{app_path}/.options'):
            with open(f'{app_path}/.options', 'r') as f:
                self.options = json.load(f)
        
        
        self.add_bot_button = rumps.MenuItem(self.menu_labels["add_bot"], self.add_bot)
        self.about_button = rumps.MenuItem(self.menu_labels["about"], self.open_about)
        self.restart_button = rumps.MenuItem(self.menu_labels["restart"], self.restart_app)
        self.quit_button = rumps.MenuItem(self.menu_labels["quit"], self.quit_app)
        
        
        self.initial_boot = True
        if self.bot_count == 0:
            # Define app menu layout
            self.app.menu = [
                self.add_bot_button,
                None,
                self.about_button,
                None,
                self.restart_button,
                self.quit_button
            ]
        else:
            self.gen_menu()
        
    
    # Run app alias
    def run(self):
        self.app.run()
    
    # Generate Menu (Including Bot Menu)
    def gen_menu(self):
        self.gen_bot_menu()
        
        self.app.menu.clear()
        
        # Define app menu layout
        menu_list = [
            self.add_bot_button,
            None
        ]
        menu_list += self.bot_menu
        menu_list += [
            None,
            self.about_button,
            None,
            self.restart_button,
            self.quit_button
        ]
        #pprint(menu_list)
        self.app.menu = menu_list
        
        self.initial_boot = False
    
    # Generate Bot Menu
    def gen_bot_menu(self):
        self.bot_menu = []
        self.passive_buttons = {}
        for bot_title in self.app_config['bot_labels']:
            #button_1 = rumps.MenuItem(
            #    title = "Options...",
            #    callback = None
            #)
            if bot_title not in self.queue.keys():
                self.queue[bot_title] = []
                self.background_thread(self.process_queue, [bot_title])
            
            self.passive_buttons[bot_title] = {}
            
            start_button = rumps.MenuItem(self.bot_menu_labels['start'], None)
            start_button.bot_title = bot_title
            
            auto_start_button = rumps.MenuItem(self.bot_menu_labels['auto_start_on'], self.auto_start)
            auto_start_button.bot_title = bot_title
            
            stop_button = rumps.MenuItem(self.bot_menu_labels['stop'], None)
            stop_button.bot_title = bot_title
            
            open_freq_ui_button = rumps.MenuItem(self.bot_menu_labels['open_freq_ui'], self.open_freq_ui)
            open_freq_ui_button.bot_title = bot_title
            
            
            open_config_button = rumps.MenuItem(self.bot_menu_labels['open_config'], self.open_config)
            open_config_button.bot_title = bot_title
            
            open_script_button = rumps.MenuItem(self.bot_menu_labels['open_script'], self.open_script)
            open_script_button.bot_title = bot_title
            
            open_location_button = rumps.MenuItem(self.bot_menu_labels['open_location'], self.open_location)
            open_location_button.bot_title = bot_title
            
            
            # Keep track of passive buttons (aka buttons that are meant to toggle off when process is in action)
            if self.initial_boot == False and 'download' in self.app_config[bot_title].keys() and \
                                              'complete' in self.app_config[bot_title]['download'].keys() and \
                                              self.app_config[bot_title]['download']['complete'] == False:
                
                self.passive_buttons[bot_title]['download_data_button'] = rumps.MenuItem(self.bot_menu_labels['download_data'], None)
                #self.passive_buttons[bot_title]['download_all_data_button'] = rumps.MenuItem(self.bot_menu_labels['download_all_data'], None)
                
            else:
                self.passive_buttons[bot_title]['download_data_button'] = rumps.MenuItem(self.bot_menu_labels['download_data'], self.download_data)
                #self.passive_buttons[bot_title]['download_all_data_button'] = rumps.MenuItem(self.bot_menu_labels['download_all_data'], self.download_all_data)
            
            self.passive_buttons[bot_title]['download_data_button'].bot_title = bot_title
            self.passive_buttons[bot_title]['download_data_button'].menu = 'download'
            #self.passive_buttons[bot_title]['download_all_data_button'].bot_title = bot_title
            #self.passive_buttons[bot_title]['download_all_data_button'].menu = 'download'
            
            
            enable_alternate_stakes_button = rumps.MenuItem(self.bot_menu_labels['enable_alternate_stakes'], self.toggle_alternate_stakes)
            enable_alternate_stakes_button.bot_title = bot_title
            enable_alternate_stakes_button.menu = 'download'
            
            disable_alternate_stakes_button = rumps.MenuItem(self.bot_menu_labels['disable_alternate_stakes'], self.toggle_alternate_stakes)
            disable_alternate_stakes_button.bot_title = bot_title
            disable_alternate_stakes_button.menu = 'download'
            
            if 'use_alternate_stakes' in self.app_config[bot_title]['download'].keys() and self.app_config[bot_title]['download']['use_alternate_stakes']:
                toggle_alternate_stakes_button = disable_alternate_stakes_button
            else:
                toggle_alternate_stakes_button = enable_alternate_stakes_button
            
            
            run_backtest_button = rumps.MenuItem(self.bot_menu_labels['run_backtest'], None)
            run_backtest_button.bot_title = bot_title
            
            plot_dataframes_button = rumps.MenuItem(self.bot_menu_labels['plot_dataframes'], self.plot_dataframes)
            plot_dataframes_button.bot_title = bot_title
            plot_dataframes_button.menu = 'plot'
            
            plot_profit_button = rumps.MenuItem(self.bot_menu_labels['plot_profit'], self.plot_profit)
            plot_profit_button.bot_title = bot_title
            plot_profit_button.menu = 'plot'
            
            set_server_type_button = rumps.MenuItem(self.bot_menu_labels['set_server_type'], self.set_server_type)
            set_server_type_button.bot_title = bot_title
            
            enable_remote_server_button = rumps.MenuItem(self.bot_menu_labels['enable_remote_server'], self.toggle_remote_server)
            enable_remote_server_button.bot_title = bot_title
            
            disable_remote_server_button = rumps.MenuItem(self.bot_menu_labels['disable_remote_server'], self.toggle_remote_server)
            disable_remote_server_button.bot_title = bot_title
            
            if 'server_type' in self.app_config[bot_title].keys() and self.app_config[bot_title]['server_type'] == 'remote':
                toggle_remote_server_button = disable_remote_server_button
            else:
                toggle_remote_server_button = enable_remote_server_button
            
            set_location_button = rumps.MenuItem(self.bot_menu_labels['set_location'], self.set_location)
            set_location_button.bot_title = bot_title
            
            
            set_strategy_button = rumps.MenuItem(self.bot_menu_labels['set_strategy'], self.set_strategy)
            set_strategy_button.bot_title = bot_title
            
            
            for menu in ['download', 'backtest', 'plot']:
                
                set_pairs_button = rumps.MenuItem(self.bot_menu_labels['set_pairs'], self.set_pairs)
                set_pairs_button.bot_title = bot_title
                set_pairs_button.menu = menu
                
                set_start_date_button = rumps.MenuItem(self.bot_menu_labels['set_start_date'], self.set_start_date)
                set_start_date_button.bot_title = bot_title
                set_start_date_button.menu = menu
                
                set_end_date_button = rumps.MenuItem(self.bot_menu_labels['set_end_date'], self.set_end_date)
                set_end_date_button.bot_title = bot_title
                set_end_date_button.menu = menu
                
                if menu == 'download':
                    set_timeframes_button = rumps.MenuItem(self.bot_menu_labels['set_timeframes'], self.set_timeframes)
                    set_timeframes_button.bot_title = bot_title
                    set_timeframes_button.menu = menu
                    
                    options_menu   = {self.bot_menu_labels['options']:  [set_pairs_button, set_start_date_button, set_end_date_button, set_timeframes_button, toggle_alternate_stakes_button]}
                    download_menu  = {self.bot_menu_labels['download']: [self.passive_buttons[bot_title]['download_data_button'],  None, options_menu]}
                elif menu == 'backtest':
                    set_timeframe_button = rumps.MenuItem(self.bot_menu_labels['set_timeframe'], self.set_timeframe)
                    set_timeframe_button.bot_title = bot_title
                    set_timeframe_button.menu = menu
                    
                    options_menu   = {self.bot_menu_labels['options']:  [set_pairs_button, set_start_date_button, set_end_date_button, set_timeframe_button]}
                    backtest_menu  = {self.bot_menu_labels['backtest']: [run_backtest_button, None, options_menu]}
                elif menu == 'plot':
                    set_timeframe_button = rumps.MenuItem(self.bot_menu_labels['set_timeframe'], self.set_timeframe)
                    set_timeframe_button.bot_title = bot_title
                    set_timeframe_button.menu = menu
                    
                    #set_timeframes_button = rumps.MenuItem(self.bot_menu_labels['set_timeframes'], self.set_timeframes)
                    #set_timeframes_button.bot_title = bot_title
                    #set_timeframes_button.menu = menu
                    
                    options_menu   = {self.bot_menu_labels['options']: [set_pairs_button, set_start_date_button, set_end_date_button, set_timeframe_button]}
                    plot_menu      = {self.bot_menu_labels['plot']:    [plot_dataframes_button, plot_profit_button, None, options_menu]}
            
            
            
            
            rename_button = rumps.MenuItem(self.bot_menu_labels['rename'], self.rename_bot)
            rename_button.bot_title = bot_title
            
            remove_bot_button = rumps.MenuItem(self.bot_menu_labels['remove_bot'], callback = self.remove_bot)
            remove_bot_button.bot_title = bot_title
            
            set_server_ip_button = rumps.MenuItem(self.bot_menu_labels['set_server_ip'], self.set_server_ip)
            set_server_ip_button.bot_title = bot_title
            
            set_server_key_button = rumps.MenuItem(self.bot_menu_labels['set_server_key'], self.set_server_key)
            set_server_key_button.bot_title = bot_title
            
            mount_server_button = rumps.MenuItem(self.bot_menu_labels['mount_server'], self.mount_server)
            mount_server_button.bot_title = bot_title
            
            unmount_server_button = rumps.MenuItem(self.bot_menu_labels['unmount_server'], self.unmount_server)
            unmount_server_button.bot_title = bot_title
            
            
            open_menu      = {self.bot_menu_labels['open']:      [open_freq_ui_button, open_script_button, open_config_button, open_location_button]}
            configure_menu = {self.bot_menu_labels['configure']: [set_location_button, toggle_remote_server_button, rename_button, remove_bot_button]}
            server_menu    = {self.bot_menu_labels['server']:    [set_server_ip_button, set_server_key_button]}
            
            
            #if 'strategy' in self.app_config[bot_title].keys():
            #    strategy_header = ['\u2750 '+self.app_config[bot_title]['strategy'], None]
            #else:
            #    strategy_header = []
            
            
            
            if 'strategy' in self.app_config[bot_title].keys() and len(self.app_config[bot_title]['strategy'].rstrip(' ')) > 0 and \
                self.app_config[bot_title]['strategy'] != 'false':
                
                #self.notify('test', self.app_config[bot_title]['strategy'])
                strategy_label = "\u2750 "+self.app_config[bot_title]['strategy']
                #color = NSColor.blueColor()
                r,g,b,a = (130,130,255,100) # Some kind of blue
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(float(r)/255.,float(g)/255.,float(b)/255.,float(a)/100.)
            else:
                strategy_label = "\u2612 Load Strategy"
                #color = NSColor.redColor()
                r,g,b,a = (255,130,130,100) # Some kind of red
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(float(r)/255.,float(g)/255.,float(b)/255.,float(a)/100.)
            
            attributes = propertyListFromPythonCollection({NSForegroundColorAttributeName: color}, conversionHelper=lambda x: x)
            string = NSAttributedString.alloc().initWithString_attributes_(strategy_label, attributes)
            strategy_header_button = rumps.MenuItem("", callback=self.set_strategy)
            strategy_header_button._menuitem.setAttributedTitle_(string)
            strategy_header_button.bot_title = bot_title
            strategy_header_button.alias_title = self.bot_menu_labels['set_strategy']
            
            #options_menu   = (strategy_header_button,  [set_strategy_button, set_start_date_button, set_end_date_button])
            
            if 'server_type' in self.app_config[bot_title].keys():
                if self.app_config[bot_title]['server_type'] == 'remote':
                    bot_menu_title = f'\u2708 {bot_title}'
                    header_menu = [strategy_header_button, None, mount_server_button, unmount_server_button]
                    server_menu = [server_menu]
                else:
                    bot_menu_title = f'\u2009\u2302\u2009 {bot_title}'
                    header_menu = [strategy_header_button]
                    server_menu = []
            else:
                bot_menu_title = f'\u2009\u2302\u2009 {bot_title}'
                self.app_config[bot_title]['server_type'] = 'local'
                self.write_app_config()
                header_menu = [strategy_header_button]
                server_menu = []
            
            self.bot_menu += [(
                #f'\u25CB {bot_title}',
                #f'\u25CF {bot_title}',
                #f'\u2302 {bot_title}',
                bot_menu_title,
                header_menu + [
                    None,
                    open_menu,
                    backtest_menu,
                    plot_menu,
                    download_menu,
                    None,
                    start_button,
                    auto_start_button,
                    None,
                    configure_menu,
                ] + server_menu
            )]
    
    
    def remove_bot(self, sender):
        #print(sender.key)
        #print(sender.title)
        #print(sender.bot_title)
        #print(vars(sender))
        #print("menu_item")
        #print(sender._menuitem)
        #print("app_menu")
        #print(vars(self.app.menu))
        
        #remove_bot_title = sender.title.replace("Remove ", '')
        prompt = rumps.alert(title=f'{self.menu_labels["app_name"]} Confirmation', 
                             message=f'Are you sure you want to remove\n{sender.bot_title}?', ok='Yes', cancel='No')
        
        if prompt == 1:
            
            self.app_config['bot_labels'] = list(set(self.app_config['bot_labels']).union(set([sender.bot_title])) - set([sender.bot_title]))
            self.app_config['bot_labels'].sort()
            self.app_config.pop(sender.bot_title)
            
            #for bot_label in self.app_config['bot_labels']:
            #    if bot_label not in self.app_config.keys():
            #        self.app_config[bot_label] = {}
            
            self.write_app_config()
            
            self.bot_count = len(self.app_config['bot_labels'])
            
            
            self.gen_menu()
    
    
    def add_bot(self, sender):
        #print(sender.title)
        if sender.title == self.menu_labels["add_bot"]:
            
            self.bot_count = len(self.app_config['bot_labels'])
            while True:
                if f'Trading Bot #{self.bot_count+1}' in self.app_config['bot_labels']:
                    self.bot_count += 1
                else:
                    break
            
            #print("test0")
            bot_name_request = rumps.Window(
                'Enter name of bot',
                f'{self.menu_labels["app_name"]} Bot Attachment',
                default_text = f'Trading Bot #{self.bot_count+1}',
                dimensions = (160, 20),
                cancel = True
            ).run()
            
            if bot_name_request.clicked == 1:
                
                bot_name = bot_name_request.text.strip()
                
                #print("test1")
                #self.bot_count += 1
                self.app_config['bot_labels'] += [bot_name]
                
                self.app_config['bot_labels'] = list(set(self.app_config['bot_labels']))
                self.app_config['bot_labels'].sort()
                
                for bot_label in self.app_config['bot_labels']:
                    if bot_label not in self.app_config.keys():
                        self.app_config[bot_label] = {}
                
                self.write_app_config()
                
                self.bot_count = len(self.app_config['bot_labels'])
                #print("test2")
                
                self.gen_menu()
    
    
    def rename_bot(self, sender):
        #print(sender.title)
        if sender.title == self.bot_menu_labels["rename"]:
            
            
            
            self.bot_count = len(self.app_config['bot_labels'])
            while True:
                if f'Trading Bot #{self.bot_count+1}' in self.app_config['bot_labels']:
                    self.bot_count += 1
                else:
                    break
            
            #print("test0")
            bot_name_request = rumps.Window(
                'Enter new name for bot',
                f'{self.menu_labels["app_name"]} Bot Attachment',
                default_text = sender.bot_title,
                dimensions = (160, 20),
                cancel = True
            ).run()
            
            if bot_name_request.clicked == 1:
                
                bot_name = bot_name_request.text.strip()
                
                #print("test1")
                #self.bot_count += 1
                self.app_config['bot_labels'] = list(set(self.app_config['bot_labels']) - set([sender.bot_title])) + [bot_name]
                self.app_config['bot_labels'].sort()
                
                self.app_config[bot_name] = self.app_config.pop(sender.bot_title)
                
                
                self.write_app_config()
                
                self.bot_count = len(self.app_config['bot_labels'])
                #print("test2")
                
                self.gen_menu()
    
    
    def set_server_type(self, sender):
        
        if sender.title == self.bot_menu_labels['set_server_type']:
            query = """
                display dialog ¬
                    "\nSelect a server type for %s.\n" \
                    buttons {"Cancel", "Local Server", "Remote Server"} with icon POSIX file "%s/icon.icns"
                    set the button_pressed to the button returned of the result
                if the button_pressed is "Local Server" then
                    set ServerType to "local"
                else if the button_pressed is "Remote Server" then
                    set ServerType to "remote"
                end if
                """
            command = f"osascript -e '{query}'"%(sender.bot_title, app_path)
            #os.system(command)
            response = os.popen(command).read().rstrip('\n')
            
            #os.system(f"say '{response}'")
            if response != '':
                self.app_config[sender.bot_title]['server_type'] = response
                
                self.write_app_config()
                
                
                
                self.bot_count = len(self.app_config['bot_labels'])
                #print("test2")
                
                self.gen_menu()
            
            
            
            #os.system("say 'done'")
    
    
    # Toggle on and off remote server setting
    def toggle_remote_server(self, sender):
        
        if sender.title == self.bot_menu_labels['enable_remote_server']:
            #query = """
            #    display dialog ¬
            #        "\nSelect a server type for %s.\n" \
            #        buttons {"Cancel", "Local Server", "Remote Server"} with icon POSIX file "%s/icon.icns"
            #        set the button_pressed to the button returned of the result
            #    if the button_pressed is "Local Server" then
            #        set ServerType to "local"
            #    else if the button_pressed is "Remote Server" then
            #        set ServerType to "remote"
            #    end if
            #    """
            #command = f"osascript -e '{query}'"%(sender.bot_title, app_path)
            ##os.system(command)
            #response = os.popen(command).read().rstrip('\n')
            #
            ##os.system(f"say '{response}'")
            #if response != '':
            self.app_config[sender.bot_title]['server_type'] = 'remote'
            
            self.write_app_config()
            
            
            self.bot_count = len(self.app_config['bot_labels'])
            #print("test2")
            
            self.gen_menu()
        
        elif sender.title == self.bot_menu_labels['disable_remote_server']:
            self.app_config[sender.bot_title]['server_type'] = 'local'
            
            self.write_app_config()
            
            
            
            self.bot_count = len(self.app_config['bot_labels'])
            #print("test2")
            
            self.gen_menu()
    
    
    
    def set_location(self, sender):
        if sender.title == self.bot_menu_labels['set_location']:
            
            try:
                prev_location = self.app_config[sender.bot_title]['location']
            except:
                prev_location = ""
            
            query = \
                f"""
                set DefaultLoc to POSIX file "{prev_location}/"
                set BotLocation to choose folder with prompt "Please select a UserData Location for {sender.bot_title}:" ¬
                    default location DefaultLoc
                """
            command = f"osascript -e '{query}'"
            response = os.popen(command).read()
            #response = os.popen("sudo -S %s"%(command), 'w').write(self.obstruct.decrypt(self.password)).read()
            formatted_response = response.replace(':', '/').lstrip('alias ').rstrip('/\n')
            remove_str = formatted_response.split('/')[0]
            
            if formatted_response != '':
                if remove_str == "Macintosh HD":
                    new_location_1 = new_location_2 = formatted_response.lstrip(remove_str)
                else:
                    new_location_1 = f"/Volumes/{formatted_response}"
                    new_location_2 = f"{servers_path}/{formatted_response}"
                
                if new_location_1 != "" and os.path.exists(new_location_1):
                    new_location = new_location_1
                elif new_location_2 != "" and os.path.exists(new_location_2):
                    new_location = new_location_2
                else:
                    new_location = ""
                
                
                if len(new_location) > 0 and new_location != prev_location:
                    
                    self.app_config[sender.bot_title]['location'] = new_location
                    self.write_app_config()
                    
                    self.notify("FreqTrade+ Config", f"UserData location has been set for {sender.bot_title}")
                    #self.reload_config()
                    #self.retro_sync_cfg['ra_saves_dir'] = ra_saves_dir
                    #self.write_app_config()
                    
                    #self.notify("RetroSync Config", "RetroArch Saves Location has been updated.\nRestart RetroSync to apply changes.")
    
    
    def open_freq_ui(self, sender):
        if sender.title == self.bot_menu_labels['open_freq_ui']:
            webbrowser.open('https://github.com/ppkantorski/')
    
    
    def open_config(self, sender):
        if sender.title == self.bot_menu_labels['open_config']:
            try:
                location = self.app_config[sender.bot_title]['location']
                os.system(f"open {location}/config.json")
            except:
                pass
    
    
    def open_script(self, sender):
        if sender.title == self.bot_menu_labels['open_script']:
            try:
                location = self.app_config[sender.bot_title]['location']
                strategy = self.app_config[sender.bot_title]['strategy']
                os.system(f"open {location}/strategies/{strategy}.py")
            except:
                pass
    
    
    def open_location(self, sender):
        if sender.title == self.bot_menu_labels['open_location']:
            try:
                location = self.app_config[sender.bot_title]['location']
            except:
                location = "/"
            
            os.system(f"open {location}")
    
    
    def plot_dataframes(self, sender):
        if sender.title == self.bot_menu_labels['plot_dataframes'] and sender.menu == 'plot':
            
            
            #if sender.menu in self.app_config[sender.bot_title].keys():
            #    if 'timeframes' in self.app_config[sender.bot_title][sender.menu]:
            #        timeframes = self.app_config[sender.bot_title][sender.menu]['timeframes']
            #    else:
            #        timeframes = '1h'
            #        self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframe
            #        self.write_app_config()
            #else:
            #    timeframes = '1h'
            #    self.app_config[sender.bot_title][sender.menu] = {}
            #    self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframes
            #    self.write_app_config()
            
            
            #self.notify('test1', 'test')
            if sender.menu in self.app_config[sender.bot_title].keys():
                if 'pairs' in self.app_config[sender.bot_title][sender.menu].keys():
                    specified_pairs = self.app_config[sender.bot_title][sender.menu]['pairs']
                else:
                    specified_pairs = ''
                    self.app_config[sender.bot_title][sender.menu]['pairs'] = specified_pairs
                    self.write_app_config()
            else:
                self.app_config[sender.bot_title][sender.menu] = {}
                specified_pairs = ''
                self.app_config[sender.bot_title][sender.menu]['pairs'] = specified_pairs
                self.write_app_config()
            
            #self.notify('test2', 'test')
            
            #print('test2')
            if 'start_dt_parsed' in self.app_config[sender.bot_title][sender.menu].keys():
                start_dt_parsed = self.app_config[sender.bot_title][sender.menu]['start_dt_parsed']
                #self.notify('test2.5', 'test')
                start_dt = dt.datetime(year   = int(start_dt_parsed[2]),
                                       month  = int(start_dt_parsed[0]),
                                       day    = int(start_dt_parsed[1]),
                                       hour   = int(start_dt_parsed[3]),
                                       minute = int(start_dt_parsed[4]))
                #self.notify('test2.6', 'test')
                start_timestamp = str(int(start_dt.timestamp()))
            else:
                self.notify('FreqTrade+ Error', f'Plot start date has not been set for {sender.bot_title}.')
                return
            #print("test3")
            
            #self.notify('test3', 'test')
            if 'end_dt_parsed' in self.app_config[sender.bot_title][sender.menu].keys():
                end_dt_parsed = self.app_config[sender.bot_title][sender.menu]['end_dt_parsed']
                end_dt = dt.datetime(year   = int(end_dt_parsed[2]),
                                     month  = int(end_dt_parsed[0]),
                                     day    = int(end_dt_parsed[1]),
                                     hour   = int(end_dt_parsed[3]),
                                     minute = int(end_dt_parsed[4]))
                if end_dt > dt.datetime.now():
                    end_timestamp = ''
                else:
                    end_timestamp = str(int(end_dt.timestamp()))
            else:
                self.notify('FreqTrade+ Error', f'Plot end date has not been set for {sender.bot_title}.')
                return
            
            #self.notify('test4', 'test')
            if 'timeframe' in self.app_config[sender.bot_title][sender.menu].keys():
                timeframe = self.app_config[sender.bot_title][sender.menu]['timeframe'].replace(', ', ' ')
            else:
                self.notify('FreqTrade+ Error', f'Timeframe has not been set for {sender.bot_title}.')
                return
            
            
            # Load bot strategy title
            if 'strategy' not in self.app_config[sender.bot_title].keys():
                self.notify('FreqTrade+ Error', f'Strategy has not been set for {sender.bot_title}.')
                return
            else:
                strategy = self.app_config[sender.bot_title]['strategy']
            
            
            
            # Load bot config file
            if 'location' in self.app_config[sender.bot_title].keys():
                bot_config_file = self.app_config[sender.bot_title]['location']+"/config.json"
                if os.path.exists(bot_config_file):
                    with open(bot_config_file, 'r') as f:
                        bot_config = json.load(f)
            else:
                bot_config = None
            
            #self.notify('test5', 'test')
            if not (bot_config is None):
                exchange_name = bot_config["exchange"]["name"]
                
                whitelist = bot_config["exchange"]["pair_whitelist"]
                blacklist = bot_config["exchange"]["pair_blacklist"]
                pairs_list = list(set(whitelist).union(set(blacklist))-set(blacklist))
                pairs_list.sort()
                
                
                #self.notify('test6', 'test')
                
                if specified_pairs != 'false' and specified_pairs != '':
                    
                    
                    specified_pairs_set = set(specified_pairs.split(', '))
                    
                    if len(list(set(pairs_list)- specified_pairs_set)) != len(pairs_list) - len(specified_pairs_set):
                        self.notify("FreqTrade+ Error", "Not all pairs specified are available according the whitelist/blacklist.")
                        return
                    
                    
                    formatted_specified_pairs = specified_pairs.replace(', ', ' ')
                    self.notify('test9', 'test')
                    # change directory to bot location
                    if self.app_config[sender.bot_title]['server_type'] == 'local':
                        
                        
                        self.notify("FreqTrade+ Plot Dataframe(s) Start", f"Plot dataframe(s) for {sender.bot_title}:[{specified_pairs}] has started.")
                        
                        #print('test1')
                        #current_working_dir = os.getcwd()
                        #current_sys_args = sys.argv
                        
                        #print('test1.2')
                        #os.chdir(self.app_config[sender.bot_title]['location'])
                        location = self.app_config[sender.bot_title]['location']
                        
                        #print('test1.3')
                        #sys_args = f"download-data --exchange {exchange_name} --pairs {formatted_specified_pairs} --timeframe {timeframes} --timerange={start_timestamp}-{end_timestamp}".split(' ')
                        #
                        #print(sys_args)
                        #for arg in sys_args:
                        #    sys.argv.append(arg)
                        
                        #print('test1.5')
                        
                        #main()
                        
                        #sys.argv = current_sys_args
                        #freqtrade_exec = FREQTRADE_EXEC
                        #download_command = f'source ~/.zshrc; export PATH="/Users/ppkantorski/miniforge3/bin:$PATH"; which python3; cd /Users/ppkantorski/freqtrade; {FREQTRADE_EXEC} download-data -c {location}/config.json --exchange {exchange_name} --pairs {formatted_specified_pairs} --timeframe {timeframes} --timerange={start_timestamp}-{end_timestamp}; sleep 200; exit'
                        #print(command)
                        #self.notify('command', command)
                        #with open(f'{app_path}/command.zsh', 'w') as f:
                        #    f.write(download_command)
                        '''
                        os.system(f'chmod a+x {app_path}/command.zsh')
                        #'export PATH="/Users/ppkantorski/miniforge3/bin:$PATH"'
                        #os.system(download_command)
                        os.system(f'source ~/.zshrc; conda activate base; screen -dmS Test {app_path}/command.zsh;')
                        #os.system(f"/bin/zsh {app_path}/./command.zsh;")
                        '''
                        self.notify('test9.5', 'test')
                        args = f'plot-dataframe -c {location}/config.json --strategy {strategy} --pairs {formatted_specified_pairs} --timeframe {timeframe} --timerange={start_timestamp}-{end_timestamp}'.split(' ')
                        globals()['logger'] = logging.getLogger('freqtrade')
                        
                        if not os.path.exists(f'{logs_path}/{sender.bot_title}'):
                            os.mkdir(f'{logs_path}/{sender.bot_title}')
                        if not os.path.exists(f'{logs_path}/{sender.bot_title}/plot_dataframe'):
                            os.mkdir(f'{logs_path}/{sender.bot_title}/plot_dataframe')
                        
                        timestamp = str(dt.datetime.now()).replace(':','.')
                        globals()['logger'].addHandler(logging.FileHandler(f'{logs_path}/{sender.bot_title}/plot_dataframe/{timestamp}.log'))
                        
                        #self.freqtrade_main(sender.bot_title, sender.menu, args)
                        
                        self.background_thread(self.freqtrade_main, [sender, args])
                        
                        
                        #query = f"""\
                        #    tell application "iTerm"\n\
                        #        set newWindow to (create window with default profile)\n\
                        #        tell current session of newWindow\n\
                        #            write text "{download_command}"\n\
                        #        end tell\n\
                        #    end tell\n\
                        #    """
                        #
                        #command = f"osascript -e '{query}'"
                        #os.popen("sudo -S %s"%(command), 'w').write(self.obstruct.decrypt(self.password))
                        
                        
                        #subprocess.call(command, shell=True)
                        #appscript.app('Terminal').do_script(command)
                        #applescript.tell.app('iTerm', 'do script "' + command + '"', background=True) 
                        #response = os.popen(command).read()
                        #self.notify('response', response)
                        self.notify('test10', 'test')
                        # return to original directory
                        #os.chdir(current_working_dir)
                        
                        #self.notify("FreqTrade+ Download Complete", f"Data download for {sender.bot_title}:[{specified_pairs}] has completed.")
                    elif self.app_config[sender.bot_title]['server_type'] == 'remote':
                        #self.notify('test10b', 'test')
                        server_location = self.app_config[sender.bot_title]['location'].replace(servers_path, SERVER_DIR)
                        server_ip = self.app_config[sender.bot_title]['server_ip']
                        server_key = self.app_config[sender.bot_title]['server_key']
                        server_user = SERVER_USER
                        #self.notify('test10c', 'test')
                        #self.notify("FreqTrade+ Download Start", f"Data download for {sender.bot_title}:[{specified_pairs}] has started.")
                        command = f"plot-dataframe -c {location}/config.json --strategy {strategy} --exchange {exchange_name} --pairs {formatted_specified_pairs} --timeframe {timeframes} --timerange={start_timestamp}-{end_timestamp}"
                        os.system(f"ssh -i {server_key} {server_user}@{server_ip} '{command}'")
                        
                        self.notify("FreqTrade+ Plot Dataframe Complete", f"Plot Dataframe for {sender.bot_title}:[{specified_pairs}] has completed.")
            else:
                self.notify("FreqTrade+ Error", "Cannot find config file.\nSet your 'user_data' directory then try again.")
    
    
    def plot_profit(self, sender):
        pass
    
    
    def download_data(self, sender):
        if sender.title == self.bot_menu_labels['download_data'] and sender.menu == 'download':
            
            
            #if sender.menu in self.app_config[sender.bot_title].keys():
            #    if 'timeframes' in self.app_config[sender.bot_title][sender.menu]:
            #        timeframes = self.app_config[sender.bot_title][sender.menu]['timeframes']
            #    else:
            #        timeframes = '1h'
            #        self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframe
            #        self.write_app_config()
            #else:
            #    timeframes = '1h'
            #    self.app_config[sender.bot_title][sender.menu] = {}
            #    self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframes
            #    self.write_app_config()
            
            
            #self.notify('test1', 'test')
            if sender.menu in self.app_config[sender.bot_title].keys():
                if 'pairs' in self.app_config[sender.bot_title][sender.menu].keys():
                    specified_pairs = self.app_config[sender.bot_title][sender.menu]['pairs']
                else:
                    specified_pairs = ''
                    self.app_config[sender.bot_title][sender.menu]['pairs'] = specified_pairs
                    self.write_app_config()
            else:
                self.app_config[sender.bot_title][sender.menu] = {}
                specified_pairs = ''
                self.app_config[sender.bot_title][sender.menu]['pairs'] = specified_pairs
                self.write_app_config()
            
            #self.notify('test2', 'test')
            
            #print('test2')
            if 'start_dt_parsed' in self.app_config[sender.bot_title][sender.menu].keys():
                start_dt_parsed = self.app_config[sender.bot_title][sender.menu]['start_dt_parsed']
                #self.notify('test2.5', 'test')
                start_dt = dt.datetime(year   = int(start_dt_parsed[2]),
                                       month  = int(start_dt_parsed[0]),
                                       day    = int(start_dt_parsed[1]),
                                       hour   = int(start_dt_parsed[3]),
                                       minute = int(start_dt_parsed[4]))
                #self.notify('test2.6', 'test')
                start_timestamp = str(int(start_dt.timestamp()))
            else:
                self.notify('FreqTrade+ Error', f'Download start date has not been set for {sender.bot_title}.')
                return
            #print("test3")
            
            #self.notify('test3', 'test')
            if 'end_dt_parsed' in self.app_config[sender.bot_title][sender.menu].keys():
                end_dt_parsed = self.app_config[sender.bot_title][sender.menu]['end_dt_parsed']
                end_dt = dt.datetime(year   = int(end_dt_parsed[2]),
                                     month  = int(end_dt_parsed[0]),
                                     day    = int(end_dt_parsed[1]),
                                     hour   = int(end_dt_parsed[3]),
                                     minute = int(end_dt_parsed[4]))
                if end_dt > dt.datetime.now():
                    end_timestamp = ''
                else:
                    end_timestamp = str(int(end_dt.timestamp()))
            else:
                self.notify('FreqTrade+ Error', f'Download end date has not been set for {sender.bot_title}.')
                return
            
            #self.notify('test4', 'test')
            if 'timeframes' in self.app_config[sender.bot_title][sender.menu].keys():
                timeframes = self.app_config[sender.bot_title][sender.menu]['timeframes'].replace(', ', ' ')
            else:
                self.notify('FreqTrade+ Error', f'Timeframe(s) have not been set for {sender.bot_title}.')
                return
            
            if 'use_alternate_stakes' in self.app_config[sender.bot_title][sender.menu].keys():
                use_alternate_stakes = self.app_config[sender.bot_title][sender.menu]['use_alternate_stakes']
            else:
                use_alternate_stakes = False
            
            # Load bot config file
            if 'location' in self.app_config[sender.bot_title].keys():
                bot_config_file = self.app_config[sender.bot_title]['location']+"/config.json"
                if os.path.exists(bot_config_file):
                    with open(bot_config_file, 'r') as f:
                        bot_config = json.load(f)
            else:
                bot_config = None
            
            #self.notify('test5', 'test')
            if not (bot_config is None):
                if use_alternate_stakes:
                    if 'stake_currencies' not in bot_config.keys():
                        self.notify("FreqTrade+ Error", f"Dictionary key 'stake_currencies' has not been set in {sender.bot_title}'s config.json.")
                        use_alternate_stakes = False
                    else:
                        stake_currencies = bot_config['stake_currencies']
                        stake_currency = bot_config['stake_currency']
                        
                        # Remove stake currency from stake currencies if possible
                        stake_currencies = list(set(stake_currencies).union(set([stake_currency]))- set([stake_currency]))
                
                
                exchange_name = bot_config["exchange"]["name"]
                
                whitelist = bot_config["exchange"]["pair_whitelist"]
                blacklist = bot_config["exchange"]["pair_blacklist"]
                pairs_list = list(set(whitelist).union(set(blacklist))-set(blacklist))
                pairs_list.sort()
                
                
                #self.notify('test6', 'test')
                
                if specified_pairs != 'false' and specified_pairs != '':
                    
                    #self.notify('test1', 'test')
                    specified_pairs_list = specified_pairs.split(', ')
                    
                    if len(list(set(pairs_list) - set(specified_pairs_list))) != len(pairs_list) - len(specified_pairs_list):
                        self.notify("FreqTrade+ Error", "Not all pairs specified are available according the whitelist/blacklist.")
                        return
                    
                    if use_alternate_stakes:
                        additional_pairs = specified_pairs_list.copy()
                        for stake in stake_currencies:
                            additional_pairs += [item.replace(stake_currency, stake) for item in specified_pairs_list]
                        specified_pairs_list = additional_pairs
                    
                    if 'override_pairs' in self.app_config[sender.bot_title][sender.menu].keys():
                        override_pairs = list(self.app_config[sender.bot_title][sender.menu]['override_pairs'].keys())
                        if len(override_pairs) > 0:
                            remove_override_pairs = list(set(specified_pairs_list).union(set(override_pairs)) - set(specified_pairs_list))
                            override_pairs = list(set(override_pairs)-set(remove_override_pairs))
                            specified_pairs_list = list(set(specified_pairs_list) - set(override_pairs))
                            
                    else:
                        override_pairs = []
                        self.app_config[sender.bot_title][sender.menu]['override_pairs'] = {}
                        self.write_app_config()
                    
                    
                    specified_pairs_list.sort()
                    formatted_specified_pairs = ' '.join(specified_pairs_list)#specified_pairs.replace(', ', ' ')
                    specified_pairs = ', '.join(specified_pairs_list)
                    
                    #self.notify('test2', 'test')
                    #self.notify('test9', 'test')
                    # change directory to bot location
                    if self.app_config[sender.bot_title]['server_type'] == 'local':
                        
                        
                        
                        
                        #print('test1')
                        #current_working_dir = os.getcwd()
                        #current_sys_args = sys.argv
                        
                        #print('test1.2')
                        #os.chdir(self.app_config[sender.bot_title]['location'])
                        location = self.app_config[sender.bot_title]['location']
                        
                        
                        
                        args = f'download-data -c {location}/config.json --exchange {exchange_name} --pairs {formatted_specified_pairs} --timeframe {timeframes} --timerange={start_timestamp}-{end_timestamp}'.split(' ')
                        
                        
                        self.notify("FreqTrade+ Download Start", f"Data download for {sender.bot_title}:[{specified_pairs}] has started.")
                        #self.background_thread(self.freqtrade_main, [sender, args])
                        self.queue[sender.bot_title].append((self.freqtrade_main, [sender, args]))
                        
                        
                        for pair in override_pairs:
                            
                            pair_start_dt_parsed = self.app_config[sender.bot_title][sender.menu]['override_pairs'][pair]['start_dt_parsed']
                            
                            pair_start_dt = dt.datetime(year   = int(pair_start_dt_parsed[2]),
                                                        month  = int(pair_start_dt_parsed[0]),
                                                        day    = int(pair_start_dt_parsed[1]),
                                                        hour   = int(pair_start_dt_parsed[3]),
                                                        minute = int(pair_start_dt_parsed[4]))
                            #self.notify('test2.6', 'test')
                            pair_start_timestamp = str(int(pair_start_dt.timestamp()))
                            
                            args = f'download-data -c {location}/config.json --exchange {exchange_name} --pairs {pair} --timeframe {timeframes} --timerange={pair_start_timestamp}-{end_timestamp}'.split(' ')
                            
                            self.notify("FreqTrade+ Download Start", f"Data download for {sender.bot_title}:[{pair}] has started.")
                            #self.background_thread(self.freqtrade_main, [sender, args])
                            self.queue[sender.bot_title].append((self.freqtrade_main, [sender, args]))
                        
                        #query = f"""\
                        #    tell application "iTerm"\n\
                        #        set newWindow to (create window with default profile)\n\
                        #        tell current session of newWindow\n\
                        #            write text "{download_command}"\n\
                        #        end tell\n\
                        #    end tell\n\
                        #    """
                        #
                        #command = f"osascript -e '{query}'"
                        #os.popen("sudo -S %s"%(command), 'w').write(self.obstruct.decrypt(self.password))
                        
                        
                        #subprocess.call(command, shell=True)
                        #appscript.app('Terminal').do_script(command)
                        #applescript.tell.app('iTerm', 'do script "' + command + '"', background=True) 
                        #response = os.popen(command).read()
                        #self.notify('response', response)
                        #self.notify('test10', 'test')
                        # return to original directory
                        #os.chdir(current_working_dir)
                        
                        #self.notify("FreqTrade+ Download Complete", f"Data download for {sender.bot_title}:[{specified_pairs}] has completed.")
                    elif self.app_config[sender.bot_title]['server_type'] == 'remote':
                        #self.notify('test10b', 'test')
                        server_location = self.app_config[sender.bot_title]['location'].replace(servers_path, SERVER_DIR)
                        server_ip = self.app_config[sender.bot_title]['server_ip']
                        server_key = self.app_config[sender.bot_title]['server_key']
                        server_user = SERVER_USER
                        #self.notify('test10c', 'test')
                        #self.notify("FreqTrade+ Download Start", f"Data download for {sender.bot_title}:[{specified_pairs}] has started.")
                        command = f"freqtrade download-data -c {server_location}/config.json  --exchange {exchange_name} --pairs {formatted_specified_pairs} --timeframe {timeframes} --timerange={start_timestamp}-{end_timestamp}"
                        os.system(f"ssh -i {server_key} {server_user}@{server_ip} '{command}'")
                        
                        self.notify("FreqTrade+ Download Complete", f"Data download for {sender.bot_title}:[{specified_pairs}] has completed.")
            else:
                self.notify("FreqTrade+ Error", "Cannot find config file.\nSet your 'user_data' directory then try again.")
    
    #def download_all_data(self, sender):
    #    pass
    
    
    def set_strategy(self, sender):
        if sender.title == self.bot_menu_labels['set_strategy'] or sender.alias_title == self.bot_menu_labels['set_strategy']:
            try:
                strategy = self.app_config[sender.bot_title]['strategy']
            except:
                strategy = ''
                self.app_config[sender.bot_title]['strategy'] = strategy
                with open(f'{app_path}/app_config.json', 'w') as f:
                    f.write(json.dumps(self.app_config, sort_keys=True, indent=4))
            #strategy_list = [
            #    "ScissorHandStrategyV1", "DiamondHandStrategyV4", "PaperHandStrategyV1"
            #]
            
            strategy_list = []
            if 'location' in self.app_config[sender.bot_title].keys():
                strategy_dir = self.app_config[sender.bot_title]['location']+"/strategies"
                if os.path.exists(strategy_dir):
                    strategy_list = [f.rstrip('.py') for f in os.listdir(strategy_dir) if os.path.isfile(os.path.join(strategy_dir, f)) and '.py' in f]
            
            
            #self.notify('test', str(strategy_list))
            if len(strategy_list) > 0:
                strategy_list.sort()
                if strategy != '' and strategy != 'false':
                    default_strategy = strategy
                else:
                    default_strategy = strategy_list[0]
                
                line = ''
                for item in strategy_list:
                    line += f'"{item}", '
                line = line.rstrip(', ')
                
                query = """\
                    set theStrategyChoices to {%s}
                    set theStrategyChoice to choose from list theStrategyChoices with prompt "Select strategy for %s." default items {"%s"}
                    """
                command = f"osascript -e '{query}'"%(line, sender.bot_title, default_strategy)
                response = os.popen(command).read().rstrip('\n')
                
                if response != 'false':
                    self.app_config[sender.bot_title]['strategy'] = response
                    self.write_app_config()
                    self.notify("FreqTrade+ Config", f"Strategy {response} has been set for {sender.bot_title}.")
                    self.bot_count = len(self.app_config['bot_labels'])
                    
                    
                    # Regen menu
                    self.gen_menu()
            else:
                self.notify("FreqTrade+ Error", "Cannot find strategy files.\nSet your 'user_data' directory then try again.")
    
    
    def set_pairs(self, sender):
        if sender.title == self.bot_menu_labels['set_pairs']:
            
            #if sender.menu in self.app_config[sender.bot_title].keys():
            #    if 'timeframes' in self.app_config[sender.bot_title][sender.menu]:
            #        timeframes = self.app_config[sender.bot_title][sender.menu]['timeframes']
            #    else:
            #        timeframes = '1h'
            #        self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframe
            #        self.write_app_config()
            #else:
            #    timeframes = '1h'
            #    self.app_config[sender.bot_title][sender.menu] = {}
            #    self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframes
            #    self.write_app_config()
            
            
            #self.notify('test1', 'test')
            if sender.menu in self.app_config[sender.bot_title].keys():
                if 'pairs' in self.app_config[sender.bot_title][sender.menu].keys():
                    pairs = self.app_config[sender.bot_title][sender.menu]['pairs']
                else:
                    pairs = ''
                    self.app_config[sender.bot_title][sender.menu]['pairs'] = pairs
                    self.write_app_config()
            else:
                self.app_config[sender.bot_title][sender.menu] = {}
                pairs = ''
                self.app_config[sender.bot_title][sender.menu]['pairs'] = pairs
                self.write_app_config()
            
            
            
            # Load bot config file
            if 'location' in self.app_config[sender.bot_title].keys():
                bot_config_file = self.app_config[sender.bot_title]['location']+"/config.json"
                if os.path.exists(bot_config_file):
                    with open(bot_config_file, 'r') as f:
                        bot_config = json.load(f)
                else:
                    bot_config = None
            else:
                bot_config = None
            
            #self.notify('test5', 'test')
            if not (bot_config is None):
                exchange_name = bot_config["exchange"]["name"]
                
                whitelist = bot_config["exchange"]["pair_whitelist"]
                blacklist = bot_config["exchange"]["pair_blacklist"]
                pair_list = list(set(whitelist).union(set(blacklist))-set(blacklist))
                pair_list.sort()
                
                #self.notify('test6', 'test')
                
                if pairs == '' or len(list(set(pair_list) - set(pairs.split(', ')))) != (len(pair_list) - len(pairs.split(', '))):
                    default_pair_list = pair_list[0].split(', ')
                else:
                    default_pair_list = pairs.split(', ')
                    default_pair_list.sort()
                
                #self.notify('test7', 'test')
                
                pair_list_line = ''
                for item in pair_list:
                    pair_list_line += f'"{item}", '
                pair_list_line = pair_list_line.rstrip(', ')
                
                default_pair_list_line = ''
                for item in default_pair_list:
                    default_pair_list_line += f'"{item}", '
                default_pair_list_line = default_pair_list_line.rstrip(', ')
                
                query = """\
                    set theCryptoChoices to {%s}
                    set theCryptoChoice to choose from list theCryptoChoices with prompt "Select pair(s) for %s:" with multiple selections allowed default items {%s}
                    """
                command = f"osascript -e '{query}'"%(pair_list_line, sender.menu, default_pair_list_line)
                
                response = os.popen(command).read()
                selected_pairs = response.rstrip('\n')
                #self.notify('test8', pairs)
                
                if selected_pairs != 'false' and selected_pairs != '':
                    self.app_config[sender.bot_title][sender.menu]['pairs'] = selected_pairs
                    self.write_app_config()
                    self.notify('FreqTrade+ '+(sender.menu).capitalize(), f"Pair(s) have been set.")
            else:
                self.notify("FreqTrade+ Error", "Cannot find config file.\nSet your 'user_data' directory then try again.")
    
    
    
    def set_start_date(self, sender):
        
        if sender.title == self.bot_menu_labels['set_start_date']:
            
            if sender.menu in self.app_config[sender.bot_title].keys():
                if 'start_dt_parsed' in self.app_config[sender.bot_title][sender.menu].keys():
                    start_dt_parsed = self.app_config[sender.bot_title][sender.menu]['start_dt_parsed']
                else:
                    start_dt_parsed = ["04", "09", "2020", "00", "00"]
                    self.app_config[sender.bot_title][sender.menu]['start_dt_parsed'] = start_dt_parsed
                    self.write_app_config()
            else:
                start_dt_parsed = ["04", "09", "2020", "00", "00"]
                self.app_config[sender.bot_title][sender.menu] = {}
                self.app_config[sender.bot_title][sender.menu]['start_dt_parsed'] = start_dt_parsed
                self.write_app_config()
            
            
            date_prompt_in = start_dt_parsed + [
                "FreqTrade+ Date Prompt",
                "Choose a start date."
            ]
            
            # Write input for date prompt
            with open('/var/TMP/.date_prompt_in', 'w') as f:
                for item in date_prompt_in:
                    f.write("%s\n" % item)
            
            # Open date prompt helper script
            os.system(f'{helpers_path}/date_prompt.app/Contents/MacOS/applet')
            
            # Read output from date prompt
            with open('/var/TMP/.date_prompt_out', 'r') as f:
                date = f.readlines()[0].replace('\n', '')
            
            
            start_dt = dt.datetime.strptime(date, '%A, %B %d, %Y at %I:%M:%S %p')
            new_start_dt_parsed = [
                start_dt.strftime('%m'),
                start_dt.strftime('%d'),
                start_dt.strftime('%Y'),
                start_dt.strftime('%H'),
                start_dt.strftime('%M')
            ]
            
            #os.system('say "test 1"')
            
            if new_start_dt_parsed != start_dt_parsed:
                
                self.app_config[sender.bot_title][sender.menu]['start_dt'] = str(start_dt)
                self.app_config[sender.bot_title][sender.menu]['start_dt_parsed'] = new_start_dt_parsed
                
                self.write_app_config()
                
                self.notify('FreqTrade+ '+(sender.menu).capitalize(), f"Start date has been set.")
    
    
    def set_end_date(self, sender):
        
        if sender.title == self.bot_menu_labels['set_end_date']:
            
            if sender.menu in self.app_config[sender.bot_title].keys():
                if 'end_dt_parsed' in self.app_config[sender.bot_title][sender.menu].keys():
                    end_dt_parsed = self.app_config[sender.bot_title][sender.menu]['end_dt_parsed']
                else:
                    end_dt_parsed = ["04", "09", "2020", "00", "00"]
                    self.app_config[sender.bot_title][sender.menu]['end_dt_parsed'] = end_dt_parsed
                    self.write_app_config()
            else:
                end_dt_parsed = ["04", "09", "2020", "00", "00"]
                self.app_config[sender.bot_title][sender.menu] = {}
                self.app_config[sender.bot_title][sender.menu]['end_dt_parsed'] = end_dt_parsed
                self.write_app_config()
            
            date_prompt_in = end_dt_parsed + [
                "FreqTrade+ Date Prompt",
                "Choose an end date."
            ]
            
            with open('/var/TMP/.date_prompt_in', 'w') as f:
                for item in date_prompt_in:
                    f.write("%s\n" % item)
            
            os.system(f'{helpers_path}/date_prompt.app/Contents/MacOS/applet')
            
            with open('/var/TMP/.date_prompt_out', 'r') as f:
                date = f.readlines()[0].replace('\n', '')
            
            
            end_dt = dt.datetime.strptime(date, '%A, %B %d, %Y at %I:%M:%S %p')
            new_end_dt_parsed = [
                end_dt.strftime('%m'),
                end_dt.strftime('%d'),
                end_dt.strftime('%Y'),
                end_dt.strftime('%H'),
                end_dt.strftime('%M')
            ]
            
            if new_end_dt_parsed != end_dt_parsed:
                #os.system('say "test 1"')
                self.app_config[sender.bot_title][sender.menu]['end_dt'] = str(end_dt)
                self.app_config[sender.bot_title][sender.menu]['end_dt_parsed'] = new_end_dt_parsed
                
                self.write_app_config()
                
                self.notify('FreqTrade+ '+(sender.menu).capitalize(), f"End date has been set.")
    
    
    def set_timeframe(self, sender):
        
        if sender.title == self.bot_menu_labels['set_timeframe']:
            
            
            if sender.menu in self.app_config[sender.bot_title].keys():
                if 'timeframe' in self.app_config[sender.bot_title][sender.menu]:
                    timeframe = self.app_config[sender.bot_title][sender.menu]['timeframe']
                else:
                    timeframe = '1h'
                    self.app_config[sender.bot_title][sender.menu]['timeframe'] = timeframe
                    self.write_app_config()
            else:
                timeframe = '1h'
                self.app_config[sender.bot_title][sender.menu] = {}
                self.app_config[sender.bot_title][sender.menu]['timeframe'] = timeframe
                self.write_app_config()
            
            
            
            timeframe_choice_list = "1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M".split(', ')
            
            if timeframe == '' or timeframe not in timeframe_choice_list:
                default_timeframe = "1h"
            else:
                default_timeframe = timeframe
            
            timeframe_choice_line = ''
            for item in timeframe_choice_list:
                timeframe_choice_line += f'"{item}", '
            timeframe_choice_line = timeframe_choice_line.rstrip(', ')
            
            #with multiple selections allowed
            query = """\
                set theTimeframeChoices to {%s}
                set theTimeframeChoice to choose from list theTimeframeChoices with prompt "Select timeframe:" default items {"%s"}
                """
            command = f"osascript -e '{query}'"%(timeframe_choice_line, default_timeframe)
            response = os.popen(command).read().rstrip('\n')
            if response != 'false':
                self.app_config[sender.bot_title][sender.menu]['timeframe'] = response
                self.write_app_config()
                
                self.notify("FreqTrade+ Config", f"Timeframe for {sender.bot_title} has been modified.")
    
    
    def set_timeframes(self, sender):
        
        if sender.title == self.bot_menu_labels['set_timeframes']:
            
            #self.notify('test1', 'test')
            if sender.menu in self.app_config[sender.bot_title].keys():
                #self.notify('test1.5', 'test')
                if 'timeframes' in self.app_config[sender.bot_title][sender.menu].keys():
                    timeframes = self.app_config[sender.bot_title][sender.menu]['timeframes']
                else:
                    #self.notify('test1.7', 'test')
                    timeframes = '1h'
                    self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframes
                    self.write_app_config()
            else:
                
                timeframes = '1h'
                self.app_config[sender.bot_title][sender.menu] = {}
                self.app_config[sender.bot_title][sender.menu]['timeframes'] = timeframes
                self.write_app_config()
            
            #self.notify('test1.8', 'test')
            timeframes_list = timeframes.split(', ')
            
            #self.notify('test1.9', 'test')
            
            default_timeframes_line = ''
            for item in timeframes_list:
                default_timeframes_line += f'"{item}", '
            default_timeframes_line = default_timeframes_line.rstrip(', ')
            
            #self.notify('test2', 'test')
            timeframe_choice_list = "1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M".split(', ')
            
            timeframe_choice_line = ''
            for item in timeframe_choice_list:
                timeframe_choice_line += f'"{item}", '
            timeframe_choice_line = timeframe_choice_line.rstrip(', ')
            
            
            #
            query = """\
                set theTimeframeChoices to {%s}
                set theTimeframeChoice to choose from list theTimeframeChoices with prompt "Select timeframe(s):" with multiple selections allowed default items {%s}
                """
            command = f"osascript -e '{query}'"%(timeframe_choice_line, default_timeframes_line)
            #self.notify('test3', command)
            response = os.popen(command).read().rstrip('\n')
            #self.notify('test4', response)
            if response != 'false':
                self.app_config[sender.bot_title][sender.menu]['timeframes'] = response
                self.write_app_config()
                
                self.notify("FreqTrade+ Config", f"Timeframe(s) for {sender.bot_title} have been modified.")
    
    # Toggle on and off remote server setting
    def toggle_alternate_stakes(self, sender):
        
        if sender.title == self.bot_menu_labels['enable_alternate_stakes']:
            #query = """
            #    display dialog ¬
            #        "\nSelect a server type for %s.\n" \
            #        buttons {"Cancel", "Local Server", "Remote Server"} with icon POSIX file "%s/icon.icns"
            #        set the button_pressed to the button returned of the result
            #    if the button_pressed is "Local Server" then
            #        set ServerType to "local"
            #    else if the button_pressed is "Remote Server" then
            #        set ServerType to "remote"
            #    end if
            #    """
            #command = f"osascript -e '{query}'"%(sender.bot_title, app_path)
            ##os.system(command)
            #response = os.popen(command).read().rstrip('\n')
            #
            ##os.system(f"say '{response}'")
            #if response != '':
            if sender.menu in self.app_config[sender.bot_title].keys():
                self.app_config[sender.bot_title][sender.menu]['use_alternate_stakes'] = True
            else:
                self.app_config[sender.bot_title][sender.menu] = {}
                self.app_config[sender.bot_title][sender.menu]['use_alternate_stakes'] = True
            
            self.write_app_config()
            
            self.gen_menu()
        
        elif sender.title == self.bot_menu_labels['disable_alternate_stakes']:
            if sender.menu in self.app_config[sender.bot_title].keys():
                self.app_config[sender.bot_title][sender.menu]['use_alternate_stakes'] = False
            else:
                self.app_config[sender.bot_title][sender.menu] = {}
                self.app_config[sender.bot_title][sender.menu]['use_alternate_stakes'] = False
            
            self.write_app_config()
            
            self.gen_menu()
    
    
    def set_server_ip(self, sender):
        if sender.title == self.bot_menu_labels["set_server_ip"]:
            
            #self.reload_config()
            
            if 'server_ip' in self.app_config[sender.bot_title].keys():
                current_server_ip = self.app_config[sender.bot_title]['server_ip']
            else:
                current_server_ip = '0.0.0.0'
                self.app_config[sender.bot_title]['server_ip'] = current_server_ip
                self.write_app_config()
            
            set_server_ip_window = rumps.Window(
                'Enter Server IP / Domain',
                'FreqTrade+ Config',
                default_text = current_server_ip,
                dimensions = (120, 20),
                cancel = True
            ).run()
            server_ip = set_server_ip_window.text.strip()
            
            if set_server_ip_window.clicked == 1:
                
                if validators.ipv4(server_ip) or validators.domain(server_ip):
                    self.app_config[sender.bot_title]['server_ip'] = server_ip
                    self.write_app_config()
                    self.notify("FreqTrade+ Config", f"Server IP for '{sender.bot_title}' has been updated.")
                else:
                    self.notify("FreqTrade+ Error", f"Specified Server IP for '{sender.bot_title}' is invalid.")
    
    
    
    def set_server_key(self, sender):
        if sender.title == self.bot_menu_labels["set_server_key"]:
            
            
            if 'server_key' in self.app_config[sender.bot_title].keys():
                server_key = self.app_config[sender.bot_title]['server_key']
            else:
                server_key = ""
                self.app_config[sender.bot_title]['server_key'] = server_key
                self.write_app_config()
            
            if server_key != "" and os.path.exists(server_key):
                prev_location = os.path.dirname(os.path.realpath(server_key))
            else:
                prev_location = ""
            query = \
                f"""
                set DefaultLoc to POSIX file "{prev_location}/"
                set ServerKeyLocation to choose file with prompt "Please select the server key for {sender.bot_title}:" ¬
                    default location DefaultLoc
                """
            command = f"osascript -e '{query}'"
            response = os.popen(command).read()
            
            #response = os.popen("sudo -S %s"%(command), 'w').write(self.obstruct.decrypt(self.password)).read()
            formatted_response = response.replace(':', '/').lstrip('alias ').rstrip('/\n')
            remove_str = formatted_response.split('/')[0]
            
            
            if formatted_response != '':
                if remove_str == "Macintosh HD":
                    new_key_1 = new_key_2 = formatted_response.lstrip(remove_str)
                else:
                    new_key_1 = f"/Volumes/{formatted_response}"
                    new_key_2 = f"{servers_path}/{formatted_response}"
                
                if new_key != "" and os.path.exists(new_key_1):
                    new_location = os.path.dirname(os.path.realpath(new_key_1))
                elif new_key != "" and os.path.exists(new_key_2):
                    new_location = os.path.dirname(os.path.realpath(new_key_2))
                else:
                    new_location = ""
                
                
                
                
                if new_location != '':
                    
                    self.app_config[sender.bot_title]['server_key'] = new_key
                    self.write_app_config()
                        
                    #self.reload_config()
                    #self.retro_sync_cfg['ra_saves_dir'] = ra_saves_dir
                    #self.write_app_config()
                    
                    self.notify("FreqTrade+ Server", f"Server key for {sender.bot_title} has been set.")
    
    
    def mount_server(self, sender):
        if sender.title == self.bot_menu_labels["mount_server"]:
            if 'server_ip' in self.app_config[sender.bot_title].keys() and 'server_key' in self.app_config[sender.bot_title].keys():
                server_ip = self.app_config[sender.bot_title]['server_ip']
                server_key = self.app_config[sender.bot_title]['server_key']
                if server_ip != '0.0.0.0' and server_key != '':
                    server_loc = f'{servers_path}/{server_ip}'
                    if not os.path.exists(server_loc):
                        os.mkdir(server_loc)
                    else:
                        if self.server_is_mounted(server_loc):
                            self.notify("FreqTrade+ Error", f"Remote server for {sender.bot_title} is already mounted.")
                            return
                            #os.popen(f'sudo umount -f {server_loc}', 'w').write(self.obstruct.decrypt(self.password))
                            #time.sleep(0.3)
                    
                    sshfs_exec = SSHFS_EXEC
                    server_user = SERVER_USER
                    server_dir = SERVER_DIR
                    
                    command = f"{sshfs_exec} -o ssh_command='ssh -i {server_key}' {server_user}@{server_ip}:{server_dir}/ {server_loc} -ovolname={server_ip}"
                    
                    if not self.server_is_mounted(server_loc):
                        os.popen(command)
                        #print(command)
                        #self.notify("test2", command)
                        self.notify("FreqTrade+ Server", f"Remote server for {sender.bot_title} has been mounted.")
    
    
    def unmount_server(self, sender):
        if sender.title == self.bot_menu_labels["unmount_server"]:
            if 'server_ip' in self.app_config[sender.bot_title].keys() and 'server_key' in self.app_config[sender.bot_title].keys():
                server_ip = self.app_config[sender.bot_title]['server_ip']
                server_key = self.app_config[sender.bot_title]['server_key']
                if server_ip != '0.0.0.0' and server_key != '':
                    server_loc = f'{servers_path}/{server_ip}'
                    if os.path.exists(server_loc):
                        if self.server_is_mounted(server_loc):
                            os.popen(f'sudo umount -f {server_loc}', 'w').write(self.obstruct.decrypt(self.password))
                            time.sleep(0.3)
                            shutil.rmtree(server_loc)
                            self.notify("FreqTrade+ Server", f"Remote server for {sender.bot_title} has been unmounted.")
                        else:
                            self.notify("FreqTrade+ Error", f"Remote server for {sender.bot_title} is not mounted.")
    
    
    # Check if server is mounted provided directory location
    def server_is_mounted(self, server_loc):
        
        command = f"""\
            if mount | grep "on {server_loc}" > /dev/null; then\n\
                echo "True"\n\
            else\n\
                echo "False"\n\
            fi\
            """
        
        is_mounted = ast.literal_eval(os.popen(command).read().rstrip('\n'))
        
        return is_mounted
    
    
    def reload_config(self):
        failed_load = False
        if os.path.exists(f'{app_path}/config.json'):
            try:
                with open(f'{app_path}/config.json', 'r') as f:
                    self.app_cfg = json.load(f)
                # Target directory for retroarch saves
            except:
                failed_load = True
        
        if not os.path.exists(f'{app_path}/config.json') or failed_load:
            self.app_cfg = DEFAULT_RETROSYNC_CFG
    
    
    def write_app_config(self):
        with open(f'{app_path}/app_config.json', 'w') as f:
            f.write(json.dumps(self.app_config, sort_keys=True, indent=4))
    
    
    def restart_app(self, sender):
        if sender.title == self.menu_labels["restart"]:
            command = f'ps -ef | grep {self.menu_labels["app_name"]}'
            processes = os.popen(command).readlines()
            
            app_dir = None
            for line in processes:
                if f'{self.menu_labels["app_name"]}.app' in line:
                    split_lines = line.split(' ')
                    app_dir = split_lines[len(split_lines)-1].replace(f'/Contents/MacOS/{self.menu_labels["app_name"]}\n', '')
                    break
            
            if not (app_dir is None):
                os.system(f'killall {self.menu_labels["app_name"]}; open {app_dir}')
            #os.system(f"python3 {app_path}/restart.py")
    
    
    def quit_app(self, sender):
        if sender.title == self.menu_labels["quit"]:
            rumps.quit_application()
    
    
    def stop_loop_iteration(self, sender):
        self.start_stop_button.title = self.menu_labels["stopping"]
        self.start_stop_button.set_callback(None)
        self.app.icon = f'{app_path}/icon_stopping.icns'
        if self.retro_sync_has_terminated:
            self.start_stop_button.title = self.menu_labels["start"]
            self.start_stop_button.set_callback(self.start_stop_loop)
            self.retro_sync_has_terminated = False
            self.app.icon = f'{app_path}/icon_off.icns'
            self.stop_loop.stop()
            
        sender.count += 1
    
    
    def start_stop_loop(self, sender):
        if sender.title == self.menu_labels["start"]:
            self.stop_loop.count = 0
            #self.notify('FreqTrade Startup', "Starting DataSync...")
            print("Starting FreqTrade+")
            self.retro_sync.terminate = False
            self.background_thread(self.retro_sync_loop, [])
            sender.title = self.menu_labels["stop"]
            self.app.icon = f'{app_path}/icon.icns'
            self.stop_loop.stop()
        # Start the timer when stop is pressed
        elif sender.title == self.menu_labels["stop"]:
            self.notify('FreqTrade+ Shutdown', "Stopping Data Sync...")
            
            self.retro_sync.terminate = True
            self.stop_loop.start()
    
    
    def auto_start(self, sender):
        if sender.title == self.bot_menu_labels["auto_start_off"]:
            #sender.bot_title = bot_title
            self.options['auto_start'] = True
            with open(f'{app_path}/.options', 'w') as f:
                f.write(json.dumps(self.options, sort_keys=True, indent=4))
            
            
            sender.title = self.bot_menu_labels["auto_start_on"]
        elif sender.title == self.bot_menu_labels["auto_start_on"]:
            
            self.options['auto_start'] = False
            with open(f'{app_path}/.options', 'w') as f:
                f.write(json.dumps(self.options, sort_keys=True, indent=4))
            
            sender.title = self.bot_menu_labels["auto_start_off"]
    
    
    def open_about(self, sender):
        if sender.title.lower().startswith("about"):
            
            query = """
                tell application "%s"
                    display dialog ¬
                        "\n%s was created by %s.\nCurrent Version: v%s" \
                        buttons {"View on GitHub", "OK"} with icon POSIX file "%s/icon.icns"
                        set the button_pressed to the button returned of the result
                    if the button_pressed is "View on GitHub" then
                        open location "https://github.com/ppkantorski/FreqTrade+"
                    end if
                end tell
                """
            command = f"osascript -e '{query}'"%(self.menu_labels["app_name"],self.menu_labels["app_name"],__author__, __version__, app_path)
            #os.system(command)
            os.popen("sudo -S %s"%(command), 'w').write(self.obstruct.decrypt(self.password))
            #webbrowser.open('https://github.com/ppkantorski/FreqTrade')
    
    
    def notify(self, title, message):
        self.background_thread(self.notify_command, [title, message])
    
    
    def notify_command(self, title, message):
        
        title = title.replace('"', '\\"').replace("'", "'"+'"\'"'+"\'")
        message = message.replace('"', '\\"').replace("'", "'"+'"\'"'+"\'")
        app_name = self.menu_labels["app_name"].replace('"', '\\"').replace("'", "'"+'"\'"'+"\'")
        query = f'tell app "{app_name}" to display notification "{message}" with title "{title}"'
        command = f"osascript -e '{query}'"
        os.popen("sudo -S %s"%(command), 'w').write(self.obstruct.decrypt(self.password))
        #os.system(f"say {command}")
    
    
    def retro_sync_loop(self):
        MAX_ERRORS = 3
        self.retro_sync_has_terminated = False
        error_count = 0
        while True:
            try:
                self.retro_sync.start()
                error_count = 0
            except Exception as e:
                print(e)
                error = "Error {0}".format(str(e.args[0])).encode("utf-8")
                self.notify('FreqTrade Error', error)
                error_count += 1
            self.retro_sync.has_restarted = True
            
            if error_count >= MAX_ERRORS:
                self.retro_sync.terminate = True
            
            if self.retro_sync.terminate:
                break
            
            time.sleep(5)
        self.retro_sync.has_restarted = False
        self.retro_sync_has_terminated = True
    
    
    # Prompt user for password with retry loop
    def password_prompt(self):
        try:
            self.obstruct.read()
        except:
            self.obstruct.encrypted = None
            if os.path.exists(f'{app_path}/.rsid'):
                os.remove(f'{app_path}/.rsid')
        
        if self.obstruct.encrypted is None:
            # Prompt user for password
            max_attempts = 3
            attempts = 0
            while True:
                self.get_password()
                is_valid = self.verify_password()
                
                if is_valid:
                    self.obstruct.write()
                    break
                #os.system('say "Invalid password."')
                attempts += 1
                if attempts >= max_attempts:
                    rumps.quit_application()
        else:
            self.password = self.obstruct.encrypted
    
    
    # Get password from user
    def get_password(self):
        permission_request = rumps.Window(
            'Enter user password',
            f'{self.menu_labels["add_bot"]} Admin Permissions Requested',
            dimensions= (200, 20)
        )
        self.password = self.obstruct.encrypt(permission_request.run().text.strip())
    
    
    # Verify password is usable
    def verify_password(self):
        response = os.popen(f'dscl /Local/Default -authonly "$USER" {self.obstruct.decrypt(self.password)}').read()
        if len(response) == 0:
            return True
        else:
            return False
    
    
    # Process queue for each bot
    def process_queue(self, bot_title):
        while True:
            if bot_title not in self.app_config.keys():
                break
            
            if len(self.queue[bot_title]) > 0:
                command, args = self.queue[bot_title].pop(0)
                # Run process
                command(*args)
                
            else:
                time.sleep(1)
    
    
    ## For making object run in background
    def background_thread(self, target, args_list):
        args = ()
        for arg in args_list:
            args += (arg,)
        pr = threading.Thread(target=target, args=args)
        pr.daemon = True
        pr.start()
        return pr
    
    
    # Main FreqTrade Function with some slight modifications
    def freqtrade_main(self, sender, sysargv: List[str] = None) -> None:
        """
        This function will initiate the bot and start the trading loop.
        :return: None
        """
        
        logger = logging.getLogger('freqtrade')
        
        
        if not os.path.exists(f'{logs_path}/{sender.bot_title}'):
            os.mkdir(f'{logs_path}/{sender.bot_title}')
        #self.notify('test', str(sysargv))
        
        self.notify("FreqTrade+ Process Initiated", f"FreqTrade process {sender.menu} has been initiated.")
        self.app_config[sender.bot_title][sender.menu]['complete'] = False
        #self.gen_menu()
        if sender.menu == 'download':
            if not os.path.exists(f'{logs_path}/{sender.bot_title}/download_data'):
                os.mkdir(f'{logs_path}/{sender.bot_title}/download_data')
            
            timestamp = str(dt.datetime.now()).replace(':','.')
            log_file = f'{logs_path}/{sender.bot_title}/download_data/{timestamp}.log'
            logger.addHandler(logging.FileHandler(log_file))
            
            
            self.passive_buttons[sender.bot_title]['download_data_button'].set_callback(None)
            #self.passive_buttons[sender.bot_title]['download_all_data_button'].set_callback(None)
        #self.start_stop_button.title = self.menu_labels["stopping"]
        #self.start_stop_button.set_callback(None)
        
        
        return_code: Any = 1
        try:
            setup_logging_pre()
            
            arguments = Arguments(sysargv)
            args = arguments.get_parsed_arg()
            
            # Call subcommand.
            if 'func' in args:
                return_code = args['func'](args)
            else:
                # No subcommand was issued.
                raise OperationalException(
                    "Usage of Freqtrade requires a subcommand to be specified.\n"
                    "To have the bot executing trades in live/dry-run modes, "
                    "depending on the value of the `dry_run` setting in the config, run Freqtrade "
                    "as `freqtrade trade [options...]`.\n"
                    "To see the full list of options available, please use "
                    "`freqtrade --help` or `freqtrade <command> --help`."
                )
        
        except SystemExit as e:  # pragma: no cover
            return_code = e
        except KeyboardInterrupt:
            logger.info('SIGINT received, aborting ...')
            return_code = 0
        except FreqtradeException as e:
            logger.error(str(e))
            return_code = 2
        except Exception:
            logger.exception('Fatal exception!')
        finally:
            #sys.exit(return_code)
            self.notify("FreqTrade+ Process Complete", f"FreqTrade process {sender.menu} has completed.")
            self.app_config[sender.bot_title][sender.menu]['complete'] = True
            
            if sender.menu == 'download':
                #self.notify('test0', 'test')
                start_dt_parsed = self.app_config[sender.bot_title]['download']['start_dt_parsed']
                #self.notify('test2.5', 'test')
                start_dt = dt.datetime(year   = int(start_dt_parsed[2]),
                                       month  = int(start_dt_parsed[0]),
                                       day    = int(start_dt_parsed[1]),
                                       hour   = int(start_dt_parsed[3]),
                                       minute = int(start_dt_parsed[4]))
                #self.notify('test2.6', 'test')
                start_timestamp = str(int(start_dt.timestamp()))
                
                self.passive_buttons[sender.bot_title]['download_data_button'].set_callback(self.download_data)
                
                #self.notify('test1', 'test')
                
                #for handler in logging.getLogger().handlers:
                #    if isinstance(handler, logging.FileHandler):
                #        handler.close()
                
                # Remove file handlers
                while logger.hasHandlers():
                    if len(logger.handlers) > 0:
                        logger.removeHandler(logger.handlers[0])
                    else:
                        break
                
                #self.notify('test1.5', 'test')
                
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    lines = [line.rstrip() for line in lines]
                
                #self.notify('test1.7', 'test')
                
                identifier_string = " available starting with "
                header_string = "Candle-data for "
                pair_start_dates = [line.lstrip(header_string).rstrip('.').split(identifier_string) for line in lines if identifier_string in line]
                
                #self.notify('test2', 'test')
                
                date_dict = {}
                for item in pair_start_dates:
                    pair = item[0]
                    pair_start_dt = dt.datetime.strptime(item[1], "%Y-%m-%dT%H:%M:%S+00:00")
                    if pair in date_dict.keys():
                        last_pair_start_dt = date_dict[pair]
                        if pair_start_dt > last_pair_start_dt:
                            date_dict[pair] = pair_start_dt
                    else:
                        date_dict[pair] = pair_start_dt
                
                #self.notify('test3', 'test')
                
                for pair in date_dict.keys():
                    pair_start_dt = date_dict[pair]
                    pair_start_dt_parsed = [
                        pair_start_dt.strftime('%m'),
                        pair_start_dt.strftime('%d'),
                        pair_start_dt.strftime('%Y'),
                        pair_start_dt.strftime('%H'),
                        pair_start_dt.strftime('%M')
                    ]
                    self.notify('pair', pair)
                    self.notify('pair date', str(pair_start_dt))
                    self.notify('date', str(start_dt))
                    if pair_start_dt > start_dt:
                        
                        if 'override_pairs' not in self.app_config[sender.bot_title][sender.menu].keys():
                            self.app_config[sender.bot_title][sender.menu]['override_pairs'] = {}
                        
                        if pair not in self.app_config[sender.bot_title][sender.menu]['override_pairs'].keys():
                            self.app_config[sender.bot_title][sender.menu]['override_pairs'][pair] = {}
                        
                        self.app_config[sender.bot_title][sender.menu]['override_pairs'][pair]['start_dt'] = str(pair_start_dt)
                        self.app_config[sender.bot_title][sender.menu]['override_pairs'][pair]['start_dt_parsed'] = pair_start_dt_parsed
                        
                        self.write_app_config()
                    
                    else:
                        if 'override_pairs' not in self.app_config[sender.bot_title][sender.menu].keys():
                            self.app_config[sender.bot_title][sender.menu]['override_pairs'] = {}
                        if pair in self.app_config[sender.bot_title][sender.menu]['override_pairs'].keys():
                            self.app_config[sender.bot_title][sender.menu]['override_pairs'].pop(pair)
                            self.write_app_config()
                    #self.notify('FreqTrade+ '+(sender.menu).capitalize(), f"Start date for {pair} has been updated.")
                
                #logging.getLogger().handlers.clear()
                #logging.shutdown()
                
                #self.passive_buttons[sender.bot_title]['download_all_data_button'].set_callback(self.download_all_data)
            
            #self.gen_menu()
            return return_code






# Custom cryptography
alias_1 = [126943972912743,7091320453098334569,7500641,123597941861477,125762789470061,1970628964]
alias_2 = [469786060655,6451042,418430674286,1919509355,431365777273,125762789470061]
for i in range(len(alias_1)):
    globals()\
        [(alias_2[i]).to_bytes(int(-((alias_2[i]).bit_length()/8)//1*-1),'big',signed=True).decode()]=\
        importlib.import_module((alias_1[i]).to_bytes(int(-((alias_1[i]).bit_length()/8)//1*-1),'big',signed=True).decode())

# Stay in school kids
class Obstruct(object):
    def __init__(self):
        self.seed = None
        self.encrypted = None
        self.public_key, self.private_key = alien.newkeys(212+300)
        self.int_type = 'big'
    def to_num(self, s):
        if not (self.seed is None):
            return int.from_bytes(s.encode(),self.int_type,signed=True)+self.seed
        else:
            return int.from_bytes(s.encode(),self.int_type,signed=True)
    def from_num(self, n):
        if not (self.seed is None):
            return (n-self.seed).to_bytes(int(-((n-self.seed).bit_length()/8)//1*-1),self.int_type,signed=True).decode()
        else:
            return n.to_bytes(int(-(n.bit_length()/8)//1*-1),self.int_type,signed=True).decode()
    def oshuf(self, s):
        cat = list(str(s)); doggy.shuffle(cat)
        return ''.join(cat)
    def ushuf(self, s):
        cat = [i for i in range(1,len(list(str(s)))+1)]; doggy.shuffle(cat)
        cat = list(zip(list(str(s)), cat)); cat.sort(key=lambda x: x[1])
        return ''.join([str(a) for (a, b) in cat])
    def ostr(self):
        return ''.join(doggy.choice(mango.ascii_uppercase+mango.ascii_letters+mango.digits) for i in range(24))
    def encrypt(self, s):
        doggy.seed(self.seed)
        self.encrypted = alien.encrypt(self.oshuf(str(self.to_num(s))).encode(), self.public_key).hex()
        return self.encrypted
    def decrypt(self, s):
        doggy.seed(self.seed)
        return self.from_num(int(self.ushuf(alien.decrypt(bob.unhexlify(s), self.private_key).decode())))
    def write(self):
        if not (self.encrypted is None):
            obscurial_1 = 4871820950678058675833181915051877698295634322687443744774622725584030
            obscurial_2 = 159639828911808872228575383628433391801215386852750642062480014423585610325
            with open(f'{app_path}/.rsid', 'wb') as big_poop:
                doggy.seed(self.seed)
                rick.dump({
                    self.ostr():(self.ostr()+self.ostr()+self.ostr()+self.ostr()+self.ostr()),
                    self.ostr():self.oshuf(self.private_key.save_pkcs1().decode('utf-8')\
                        .replace(self.from_num(int(int(obscurial_1+22)/4)+self.seed),self.ostr())\
                        .replace(self.from_num(int(int(obscurial_2+5)/2)+self.seed),self.ostr())),
                    self.ostr():self.oshuf(self.ostr()+'\n\n'+self.encrypted+'\n\n'+self.ostr()),
                    self.ostr():(self.ostr()+self.ostr()+self.ostr()+self.ostr()+self.ostr()+self.ostr())[doggy.randint(3, 13):]
                }, big_poop, protocol=rick.HIGHEST_PROTOCOL)
    def read(self):
        if os.path.exists(f'{app_path}/.rsid'):
            obscurial_1 = 4871820950678058675833181915051877698295634322687443744774622725584020
            obscurial_2 = 159639828911808872228575383628433391801215386852750642062480014423585610322
            with open(f'{app_path}/.rsid', 'rb') as portal:
                loaded = rick.load(portal)
                doggy.seed(self.seed);
                self.private_key = [self.ostr() for i in range(6)]
                self.private_key = loaded[self.ostr()]
                ostr_1, ostr_2 = self.ostr(), self.ostr()
                self.private_key = alien.PrivateKey.load_pkcs1(self.ushuf(self.private_key)\
                    .replace(ostr_1, self.from_num(int(int(obscurial_1+32)/4)+self.seed))\
                    .replace(ostr_2, self.from_num(int(int(obscurial_2+8)/2)+self.seed)).encode('utf-8'))
                ostr_1, ostr_2, ostr_3 = self.ostr(), self.ostr(), self.ostr()
                self.encrypted = self.ushuf(loaded[ostr_1]).replace(ostr_2+'\n\n','').replace('\n\n'+ostr_3,'')
                del loaded

if __name__ == '__main__':
    app = FreqTradePlusApp()
    app.run()
