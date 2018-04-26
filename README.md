# AutoVPN

VPN in my company requires me to enter password as ldap_password and then the OTP.
This is a solution to entering password automatically and make sure it stays connected
at all times.

## Screenshots

### System tray icon
![notifications](https://i.imgur.com/8sRHzYT.png)
### Notifications
![system_tray](https://i.imgur.com/luZEYjl.png)

## Configuration file

Location: ~/.corp_vpn.yaml

	username: arastogi
	OTP_SECRET: SECRET

## Development

	pip install -r requirements.txt
	python app.py

## Build Instructions on Mac

	make app
	# Built app should be located at: ./dist/AutoVPN.app/Contents/MacOS/AutoVPN
