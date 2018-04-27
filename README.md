# AutoVPN

Some companies (like mine) require a concatenation of ldap password and OTP as password while connecting
to VPNs. This is a solution to compute VPN password automatically by getting ldap password from keychain
and OTP via oathtool. As a bonus, it also makes sure that it retries VPN connection if it fails for some reason.

## Features

* Autoconnects VPN on startup.
* Keeps checking VPN status every second and reconnects if necessary.
* Disconnects VPN on exit

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

	make app # Builds app at: ./dist/AutoVPN.app
	make dmg # Builds dmg at ./AutoVPN.dmg
