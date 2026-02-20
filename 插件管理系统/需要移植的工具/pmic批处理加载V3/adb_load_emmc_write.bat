adb push test.sh /data/
::adb shell cd /data/
::adb shell chmod 777 test.sh
start "emmc_read" adb_load_emmc_read.bat /k
start "ddr" adb_load_ddr.bat /k
adb shell sh /data/test.sh
