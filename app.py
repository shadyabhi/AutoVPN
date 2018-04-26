import rumps
import threading
import time
import socket
import yaml
import logging
import commands
import subprocess
import os
# import sys


class App():
    """
    System Tray app to connect to VPN
    """
    def __init__(self):
        # app initially set as None to signal when app starts
        self.app = None
        self.sleep_time = 1
        self.config_path = ".corp_vpn.yaml"
        self.notification_title = "VPN"
        self.lock = threading.Lock()

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        hdlr = logging.FileHandler('/tmp/vpn.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)

        self.parse_config()

    def parse_config(self):
        cfg_location = os.path.join(os.getenv("HOME"), self.config_path)
        try:
            self.cfg = yaml.load(open(cfg_location))
            self.logger.info("Successfully parsed config file")
        except Exception:
            self.logger.exception("Error loading config file from location: {0}".format(cfg_location))

    def notify(self, title, text):
        ret, stdout = commands.getstatusoutput("""
                osascript -e 'display notification "{}" with title "{}"'""".format(text, title))
        if ret != 0:
            self.logger.fatal("Error sending notifications")

    def get_password(self):
        """
        Return password for VPN
        """
        otp_secret = self.cfg['OTP_SECRET']
        ret, otp = commands.getstatusoutput("/usr/local/bin/oathtool --totp -b {0} | tr -d \"\n\"".format(otp_secret))
        self.logger.info("Executed oathtool command: ret: {0}, output: {1}".format(ret, otp))
        if ret != 0:
            self.logger.fatal("Error getting otp")
        ret, ldap_pass = commands.getstatusoutput("""security 2>&1 > /dev/null find-generic-password -ga {0} | grep password | sed 's/password: "//' | sed 's/"$//'""".format(self.cfg["username"]))
        if ret != 0:
            self.logger.fatal("Error getting ldap password")

        return ldap_pass + otp

    def connect_vpn(self):
        """
        Connects VPN and stays on forever
        """
        now = time.time()
        self.logger.info("Executing command to start VPN")
        passwd = self.get_password()
        credentials = "{0}\\n{1}\\ny".format(self.cfg['username'], passwd)
        printf = subprocess.Popen(['printf', credentials], stdout=subprocess.PIPE)
        vpn = subprocess.Popen("/opt/cisco/anyconnect/bin/vpn -s connect vpn-abg.corp.linkedin.com".split(" "), stdin=printf.stdout, stdout=subprocess.PIPE)
        # for c in iter(lambda: vpn.stdout.read(1), ''):
        #    sys.stdout.write(c)
        stdout, stderr = vpn.communicate()
        # Sanitize stdout
        stdout = stdout.replace(passwd, "PASSWORD_SANITIZED")

        elasped = time.time() - now
        self.logger.info("VPN command executed, took: {0}, stdout: {1}, stderr: {2}".format(elasped, stdout, stderr))

        if "Another AnyConnect application is running" in stdout:
            self.notify(self.notification_title, "Another VPN agent running, stop that")
            self.logger.fatal("Another VPN client running, exit that")
        if "state: Connected" in stdout:
            notify_msg = "VPN Connected successfully in {0} seconds".format(elasped)
            self.notify(self.notification_title, notify_msg)

    def is_vpn_on(self):
        """
        Checks if VPN is on/off

        Resolves an internal DNS hostname
        """
        ret = None
        try:
            socket.gethostbyname('tools.corp.linkedin.com')
            ret = True
        except socket.gaierror:
            ret = False
        self.logger.info("VPN status: {0}".format(ret))
        return ret

    def heartbeat(self):
        while True:
            # Is app running?
            if self.app:
                if self.is_vpn_on():
                    self.app.icon = "vpn_on.png"
                else:
                    self.app.icon = "vpn_off.png"
                    self.notify(self.notification_title, "VPN was disconnected, attempting to connect...")
                    self.logger.info("Trying to connect VPN")
                    self.lock.acquire()
                    self.connect_vpn()
                    self.lock.release()

            time.sleep(self.sleep_time)

    def start_updater_thread(self):
        # Start heartbeat thread
        t = threading.Thread(target=self.heartbeat)
        self.logger.info("Starting heartbeat thread.")
        t.start()

    def disconnect_vpn(self, _):
        self.lock.acquire()
        time.sleep(self.sleep_time + 0.5)

        ret, out = commands.getstatusoutput('/opt/cisco/anyconnect/bin/vpn disconnect')
        if ret != 0:
            self.logger.fatal("Error disconnecting VPN: error: {0}".format(out))
        else:
            self.lock.release()
            self.notify(self.notification_title, "VPN disconnected")
        rumps.quit_application()

    def start_system_tray_app(self):
        self.app = rumps.App('VPN', quit_button=None)
        self.app.menu = [
            rumps.MenuItem('Quit', callback=self.disconnect_vpn),
        ]
        self.app.run()

    def run(self):
        self.start_updater_thread()
        self.start_system_tray_app()


if __name__ == "__main__":
    try:
        app = App()
        app.run()
    except Exception:
        logging.exception("Some shit happened trying to run app")
