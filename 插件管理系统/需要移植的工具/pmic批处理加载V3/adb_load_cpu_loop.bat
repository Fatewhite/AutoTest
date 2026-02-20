for /L %%i  in (1,1,8) do (
timeout /t 1 1>nul
start "cpu" adb_load_cpu.bat /k
  )
start "emmc_write" adb_load_emmc_write.bat /k
::adb shell linpack 3000 &
::start adb_load_cpu.bat /k