dev-app:
	rm -rf dist build; python setup.py py2app -A
app:
	rm -rf dist build; python setup.py py2app
dmg:
	make app
	hdiutil create ./AutoVPN.dmg -ov -volname "AutoVPN" -fs HFS+ -srcfolder "./dist"
