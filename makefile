app:
	pyinstaller --onefile --log-level WARN --icon=icon.icns --name things2taskpaper --windowed app.py
debug:
	-rm -r dist/things2taskpaper-debug.app
	-rm dist/things2taskpaper-debug
	pyinstaller --onefile --log-level WARN --icon=icon.icns --name things2taskpaper-debug --debug all --windowed app.py
	open dist/things2taskpaper-debug 
apptest:
	python --version
	echo "make sure this is Python 3!"
	python app.py
