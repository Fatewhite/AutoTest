::adb push 1khz.wav /data/1khz.wav
::adb shell avacmd media {\"type\":\"media\",\"cmd\":\"volume_set\",\"volume\":100}
::adb shell aplay /data/1khz.wav
::adb shell amixer -Dhw:audiocodec  cset name='DAC Volume' 63
::adb shell ogg123 /data/1KHz.ogg
adb push camera.sh /data/
start  "audia" adb_load_audio.bat /k
adb shell sh /data/camera.sh
pause
::adb shell
::timeout /t 5 /nobreak >nul


