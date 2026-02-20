#!/bin/sh

## 测试开始结束标志位
EMMC_FLAG=/data/emmc_flag

## 获取当前可用大小
avail_size=`df -m | grep UDISK | awk '{print $4}'`

## 获取固定Size大小
mmc_size=`df -m | grep UDISK | awk '{print $2}'`

## 读写测试以 1M 16K 4K 1K 作为块大小进行测试
count_value_1M=$mmc_size
count_value_16K=$((mmc_size*64))
count_value_4K=$((mmc_size*256))
count_value_1K=$((mmc_size*1024))

echo 1 > $EMMC_FLAG
while true
do
	echo "You can stop emmc read test by: echo off > /data/emmc_flag"
	flag=`cat $EMMC_FLAG`
	if [ $flag == "off" ]; then
		echo "emmc read test is off"
		exit 0
	fi
	
	dd if=/dev/by-name/UDISK of=/dev/null bs=1M count=${count_value_1M}
	sleep 0.5
	
	dd if=/dev/by-name/UDISK of=/dev/null bs=16K count=${count_value_16K}
	sleep 0.5
	
	dd if=/dev/by-name/UDISK of=/dev/null bs=4K count=${count_value_4K}
	sleep 0.5
	
	dd if=/dev/by-name/UDISK of=/dev/null bs=1K count=${count_value_1K}
	sleep 0.5

done
