update:
	sudo pip install -r requirements.txt
dev-app:
	rm -rf dist build; python setup.py py2app -A
app:
	rm -rf dist build; python setup.py py2app
dmg:
	make app
	rm ./AutoVPN.dmg
	hdiutil create ./AutoVPN-pre.dmg -ov -volname "AutoVPN" -fs HFS+ -srcfolder "./dist"
	hdiutil convert ./AutoVPN-pre.dmg -format UDZO -o ./AutoVPN.dmg
	rm ./AutoVPN-pre.dmg
