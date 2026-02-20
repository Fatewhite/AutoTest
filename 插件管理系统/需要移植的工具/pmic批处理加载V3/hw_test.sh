#!/bin/sh

mkdir -p /data/hw_test/result/
/data/hw_test/califile/cp_califile.sh
moudle_env()
{
   export  MODULE_CHOICE
}


module_choice()
{
    echo "****************************************************"
    echo "***                                              ***"
    echo "***        *******************                   ***"
    echo "***        ***HW TEST TOOLS***                   ***"
    echo "***        *******************                   ***"
    echo "***        *******************                   ***"
    echo "***                                              ***"
    echo "****************************************************"


    echo "*****************************************************"
    echo "ddr test :            1"
    echo "cpu test:             2"
    echo "flash test:           3"
    echo "audio test:           4"
    echo "wifi test:            5"
    echo "reboot test:          6"
    echo "camera test           7"
    echo "cpu_bpu test          8"
    echo "speech test           9"
    echo "finish test           10"
    echo "mr527 stree all       11"
    echo "*****************************************************"

    echo  "please input your test moudle: "
    #read -t 30  MODULE_CHOICE
   MODULE_CHOICE=1 
}


ddr_test()
{
    sh /data/hw_test/ddr/ddr_test.sh
}

cpu_test()
{
    sh /data/hw_test/cpu/cpu_test.sh
}

flash_test()
{
	sh /data/hw_test/flash/flash_test.sh
   
}

wifi_test()
{
    sh /data/hw_test/wifi/wifi_test.sh
}


audio_test()
{
    sh /data/hw_test/audio/audio_test.sh &
}

reboot_test()
{
    fcnt=/data/hw_test/result/reboot_cnt
    if [ -e "$fcnt" ]; then
		rm -f $fcnt
    fi
    sh /data/hw_test/reboot/reboot_test.sh
}


camera_test()
{
    sh /data/hw_test/camera/camera_test.sh
}

cpu_bpu_test()
{
    sh  /data/hw_test/bpu/cpu.sh
}

speech_test()
{
    sh /data/hw_test/speech/speech_test_choice.sh
}

mr527_stree_all()
{
    sh /data/hw_test/cpu/mr527_stress_all.sh
}

finish_test()
{
    if [ -f /mnt/misc/start.log ];then
        rm /mnt/misc/start.log
    fi
    if [ ! -s /mnt/misc/caliberation_result.json ];then
        echo "caliberation file is empty! start delete json files ..."
        rm /mnt/misc/*.json
    fi
    echo "start factory reset !"
    /usr/bin/factory_reset.sh
    echo "factory reset finish !"
}
module_test()
{
    if [[ $MODULE_CHOICE != 9 && $MODULE_CHOICE != 10 && $MODULE_CHOICE != 11 ]]; then
	    killall -9 ava
	    killall -9 performance_test.sh
        touch /tmp/ava.pid
    
    fi
    case ${MODULE_CHOICE} in
        1)
            ddr_test
            ;;
        2)
            cpu_test
            ;;
        3)
            flash_test
            ;;
        4)
            audio_test
            ;;
        5)
            wifi_test
            ;;
        6)
            reboot_test
            ;;
        7)
            camera_test
            ;;
        8)
            cpu_bpu_test
            ;;
        9)
            speech_test
            ;;
        10)
            finish_test
            ;;
        11)
            mr527_stree_all
            ;;
	esac
    if [[ $MODULE_CHOICE != 9 && $MODULE_CHOICE != 10 ]]; then
	    /data/hw_test/performance_test.sh &
    fi
}

module_choice
module_test
