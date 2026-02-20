adb push module_choice.txt /data/hw_test
timeout /t 2 1>nul
adb shell sh /usr/bin/cpu.sh userspace
adb shell "sh /data/hw_test/hw_test.sh < /data/hw_test/module_choice.txt | tee  /data/hw_test/ddr_test.log"
::adb shell nohup stressapptest -s 86400 -i 4 -C 4 -W --stop_on_errors -M 200 -l /data/hw_test/result/stressapptest.log > /dev/null 2>&1 &
pause
::memtester 180M &
::adb shell ps|grep stressapptest
::timeout /t 10 /nobreak >nul
::adb shell 







