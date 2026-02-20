::adb push ./sample_12 /data/
::adb shell chmod +x ./data/sample_12/run_test_12.sh
::adb shell vpm_run -s /data/sample_12/sample_12.txt -l 99999999 &
::adb push ./stereo_vpm_run_test /data/
start "cpu_loop" adb_load_cpu_loop.bat /k
timeout /t 3 1>nul
start "ping www.baidu.com" adb_load_wifi_ping.bat /k
::adb shell vpm_run -s /etc/npu/sample.txt -l 100000 &
adb shell chmod +x /data/stereo_vpm_run_test/run_test5.sh
adb shell sh /data/stereo_vpm_run_test/run_test5.sh
