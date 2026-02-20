::for %%i in (1,2,3,4,5,6,7,8) do (adb shell linpack 3000 &)
::start adb_load_emmc_write.bat /k
adb shell linpack 3000 &
::start adb_load_cpu2.bat /k
::echo nihao