@echo off
pip install -r requirements.txt
pyinstaller --onefile --windowed --icon=NONE --name="Todo Uygulamasi" todo.py
echo Exe dosyasi dist klasorunde olusturuldu. 