adb push 1khz.wav /data/1khz.wav
adb shell avacmd media {\"type\":\"media\",\"cmd\":\"volume_set\",\"volume\":100}
start  "wifi" adb_load_wifi.bat /k
adb shell aplay /data/1khz.wav
::adb shell amixer -Dhw:audiocodec  cset name='DAC Volume' 63
::adb shell ogg123 /data/1KHz.ogg

pause
::adb shell
::timeout /t 5 /nobreak >nul


