app:
	echo "if the app doesn't build, delete the cache folders in ~/Library/Application Support/pyinstaller"
	pyinstaller --onefile --log-level WARN --icon=icon.icns --name things2taskpaper --noconfirm --windowed app.py
	open dist/things2taskpaper.app/Contents/MacOS/things2taskpaper
debug:
	-rm -r dist/things2taskpaper-debug.app
	-rm dist/things2taskpaper-debug
	pyinstaller --onefile --log-level DEBUG --icon=icon.icns --name things2taskpaper-debug --debug all --windowed app.py
	open dist/things2taskpaper-debug.app/Contents/MacOS/things2taskpaper-debug
apptest:
	python --version
	echo "make sure this is Python 3!"
	python app.py
