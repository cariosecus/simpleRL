@echo off
echo This file will compile the source into a windows executable inside the dist/folder. By continuing you will remove the current contents of that folder.
pause
echo removing old files...
rmdir dist\ /s /q

echo installing the dependencies...
pip install tcod==11.1.1
pip install numpy==1.16.2
pip install pyYAML==5.1.2
pip install pyinstaller
pyinstaller -y -w "engine.py" --distpath=dist\ --workpath=dist\dist\engine\

echo copying files...
copy dist\engine\engine.exe dist\
copy dist\engine\python37.dll dist\
copy dist\engine\pythoncom37.dll dist\
copy dist\engine\pywintypes37.dll dist\
copy dist\engine\libopenblas.IPBC74C7KURV7CB2PKT5Z5FNR3SIBV4J.gfortran-win_amd64.dll dist\
copy dist\engine\_cffi_backend.cp37-win_amd64.pyd dist\
copy dist\engine\_ctypes.pyd dist\
copy dist\engine\_socket.pyd dist\
copy dist\engine\pyexpat.pyd dist\
copy dist\engine\select.pyd dist\
copy dist\engine\win32api.pyd dist\
copy dist\engine\base_library.zip dist\

echo copying folders...
xcopy images\* dist\images\ /S /E /Y /Q /I
xcopy data\* dist\data\ /S /E /Y /Q /I
xcopy dist\engine\numpy\* dist\numpy\ /S /E /Y /Q /I
xcopy dist\engine\tcod\* dist\tcod\ /S /E /Y /Q /I
copy dist\engine\SDL2.dll dist\tcod\x64\

echo deleting temporary files...
rmdir dist\dist\ /s /q
rmdir dist\engine\ /s /q
echo done.
pause