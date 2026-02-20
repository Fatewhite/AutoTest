# -*- coding: utf-8 -*-
import fnmatch
import time
import os
import numpy as np
import pandas as pd
from openpyxl import workbook
import matplotlib
matplotlib.use('TkAgg') # 或者 'Qt5Agg'

# for file in file list:
# with open(os.path.join(current_dir, file), 'r') as f:
# content = f.read
# print(content)


# local_time = time.localtime()
#
# print(local_time)

#*************************user input***********************#

print('*************************过流点设置************************')
i_thr = int(input("\n请输入过流点（mA）:    "))
print(f'\n================过流点为：{i_thr}mA')
#*************************user input***********************#
print('*************************工作环境选择**********************')
print('*    1.地毯                                               *')
print('*    2.硬地面                                             *')
print('***********************************************************')
get_num1 = int(input("\n请输入工作环境 ："))
if get_num1 ==1:
    work_evr = '地毯'
elif get_num1 ==2:
    work_evr = '硬地面'
else:
    work_evr = '工作环境输入无效，请重新运行程序'
print('\n================工作环境为：'+work_evr+'\n')

print('#************************过流类型选择**********************#')
print('#*    1.积分过流                                           #')
print('#*    2.瞬时堵转                                           #')
print('#*    3.弱卡滞                                             #')
print('#**********************************************************#')
get_num2 = int(input("\n请输入过流类型 ："))
if get_num2 ==1:
    work_mode = '积分过流'
elif get_num2 ==2:
    work_mode = '瞬时堵转'
elif get_num2 == 3:
    work_mode = '弱卡滞'
else:
    work_mode = "过流类型输入无效，请重新运行程序"
print('\n================过流类型为：'+work_mode)

null=input("\n输入任意键运行程序")

#查找当前文件夹下以txt结尾的文件
for f_name in os.listdir('.'):
    if fnmatch.fnmatch(f_name, '*.txt'):
        f= f_name
        # print(f_name)

#打开txt文件并删除前4行和后20行
with open(f,'r', encoding='utf-8') as file:
    data_exc = file.readlines()
    del data_exc[0:4]
    del data_exc[-20:-1]
    del data_exc[-1]

# ************************************************************************************#
#                                                                                     #
#   i_list          :                                                                 #
#   v_list          :                                                                 #
#   time_list       :                                                                 #
#   result_list     :                                                                 #
#   hour_list       :                                                                 #
#   minute_list     :                                                                 #
#   minute_list     :                                                                 #
#   second_list     :                                                                 #
#   ms_list         :                                                                 #
#   total_time_list :                                                                 #
#   time_statistic  :                                                                 #
#   line_num        :                                                                 #
#                                                                                     #
#*************************************************************************************#

#**********************************变量声明与初始化**************************************#
i_list          = []
v_list          = []
time_list       = []
result_list     = []
hour_list       = []
minute_list     = []
second_list     = []
ms_list         = []
total_time_list = []
last            = []
time_statistic  = []
cnt_list        = []
fanpwm_list     = []
line_num = len(data_exc)

for i in range(0,line_num):
    time_list.append('')
    i_list.append('')
    v_list.append('')
    result_list.append('')
    hour_list.append('')
    minute_list.append('')
    second_list.append('')
    ms_list.append('')
    total_time_list.append('')
    last.append('')
    time_statistic.append('')
    cnt_list.append('')
    fanpwm_list.append('')

# ************************************************************************************#
#                                                                                     #
#   i_list          :                                                                 #
#   v_list          :                                                                 #
#   time_list       :                                                                 #
#   fanpwm_list     :                                                                 #
#                                                                                     #
#*************************************************************************************#

#***************************************参数提取***************************************#
for i in range(0,line_num):
    time_list[i] = data_exc[i][11:23]
    for j in range(0,len(data_exc[i])):
        if data_exc[i][j:j+14]=='rollerVoltCtrl':
            v_list[i] = int(data_exc[i][j+17:j+24].strip())
        elif data_exc[i][j:j+9]=='rollI(mA)':
            i_list[i]=int((data_exc[i][j+17:j+23]).strip())
        elif data_exc[i][j:j+6] == 'fanPwm':
            fanpwn_list = int(data_exc[i][j+17:j+20].strip())

# with open('time_list.txt','w') as f_time:
#     for i in range(0,len(time_list)):
#         f_time.write(time_list[i]+'\n')

# with open('v_list.txt','w') as f_v:
#     for i in range(0,len(v_list)):
#         f_v.write(v_list[i]+'\n')

# with open('i_list.txt','w') as f_i:
#     for i in range(0,len(i_list)):
#         f_i.write(i_list[i]+'\n')

#***************************************时间换算****************************************#
for i in range(0,len(time_list)):
    for j in time_list[i]:
        hour_list[i]=time_list[i][0:2]
        minute_list[i]=time_list[i][3:5]
        second_list[i]=time_list[i][6:8]
        ms_list[i]=time_list[i][9:12]
        total_time_list[i]=float(ms_list[i])+1000*float(second_list[i])+60000*float(minute_list[i])+3600000*float(hour_list[i])

t_start = 0
state=0
c=0
flag =0
cnt = 0

if get_num2 ==1:
    c       =0
    flag    =0
    t_start =0
    cnt     =0

# ===================================积分过流分析=======================================#
#                                                                                     #
#   state = 0 : 未启动                                                                 #
#   state = 1 : 正常运行                                                               #
#   state = 2 : 正转积分过流                                                            #
#   state = 3 : 停转                                                                  #
#   state = 4 : 反转2S                                                                #
#   state = 5 : 停止运行                                                               #
#                                                                                    #
#************************************************************************************#
    for i in range(0,len(i_list)):
        if state ==0:
            result_list[i] = '未启动'
            if int(i_list[i]) >0 and int(i_list[i]) <i_thr and int(i_list[i+1])>0:
                result_list[i] = '正常运行'
                t_start = i
                state = 1
        if state ==1:
            result_list[i] = '正常运行'
            if int(v_list[i]) ==0 and int(i_list[i-1]) >0 and int(v_list[i+1]) ==0:  #修改
                result_list[i] = '停转'
                t_start = i
                state = 3
            elif int(i_list[i]) >=i_thr and int(i_list[i-1]) <i_thr and int(i_list[i+1]) >=i_thr:
                result_list[i] = '正转积分过流'
                t_start = i
                state = 2
        elif state ==2:
            result_list[i] = '正转积分过流'
            if float(i_list[i]) <i_thr:
                result_list[i]= '未过流'
            elif float(i_list[i]) >= i_thr and float(i_list[i-1])<i_thr:
                t_start = i
            if float(v_list[i]) ==0 and float(v_list[i-1])>0 and float(v_list[i+1])>0:
                result_list[i] = '异常'
            elif float(v_list[i])==0 and float(v_list[i-1]) >0 and float(v_list[i+15]) ==0 and float(v_list[i+14]) ==0:
                result_list[i] = '停止运行'
                cnt=cnt+1
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i - 1] = cnt
                t_start = i
                state=5
            elif float(v_list[i]) <0:
                cnt=cnt+1
                result_list[i] = '反转2s'
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state=4
            elif (float(v_list[i])==0 and float(v_list[i-1]))>0 or ((float(v_list[i])==0 and float(v_list[i+1]))) <0 : #and float(v_list[i+1]) ==0 :
                cnt=cnt+1
                result_list[i] = '停转'
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state=3
        elif state ==3 :
            result_list[i] = '停转'
            if float(v_list[i]) <0 and float(v_list[i-1]) ==0 and float(v_list[i+1])<0:
                result_list[i] = '反转2s'
                t_start = i
                state =4
            elif float(v_list[i]) >0 and float(v_list[i-1])==0 and float(v_list[i+1])>0 and float(i_list[i])>=i_thr:
                result_list[i] = '正转积分过流'
                t_start =i
                state=2
            elif float(v_list[i]) >0 and float(v_list[i-1])==0 and float(v_list[i+1])>0 and float(i_list[i]) <i_thr:
                result_list[i] = '正常运行'
                t_start = i
                state =1
        elif state ==4:
            result_list[i] = '反转2s'
            if float(v_list[i])>0:
                result_list[i] = '正转积分过流'
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state=2
            elif float(v_list[i]) ==0 and float(v_list[i-1])<0 :
                result_list[i] = '停转'
                time_statistic[i-1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state = 3
        elif state ==5:
            result_list[i] = '停止运行'


    # for i in range(0,len(i_list)):
    #     if state ==0:
    #         result_list[i] = '未启动'
    #         if int(i_list[i]) >0 and int(i_list[i]) <i_thr and int(i_list[i+1])>0:
    #             result_list[i] = '正常运行'
    #             t_start = i
    #             state = 1
    #     if state ==1:
    #         result_list[i] = '正常运行'
    #         if int(v_list[i]) ==0 and int(i_list[i-1]) >0 and int(v_list[i+1]) ==0:
    #             result_list[i] = '停转'
    #             t_start = i
    #             state = 3
    #         elif int(i_list[i]) >=i_thr and int(i_list[i-1]) <i_thr and int(i_list[i+1]) >=i_thr:
    #             result_list[i] = '正转积分过流'
    #             t_start = i
    #             state = 2
    #     elif state ==2:
    #         result_list[i] = '正转积分过流'
    #         if float(v_list[i])==0 and float(v_list[i-1]) >0 and float(v_list[i+15]) ==0 :
    #             result_list[i] = '停止运行'
    #             cnt=cnt+1
    #             time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
    #             cnt_list[i - 1] = cnt
    #             t_start = i
    #             state=5
    #         elif float(v_list[i])==0 and float(v_list[i-1]) >0 and float(v_list[i+1]) ==0 :
    #             cnt=cnt+1
    #             result_list[i] = '停转'
    #             time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
    #             cnt_list[i-1] = cnt
    #             t_start = i
    #             state=3
    #     elif state ==3 :
    #         result_list[i] = '停转'
    #         if float(v_list[i]) <0 and float(v_list[i-1]) ==0 and float(v_list[i+1])<0:
    #             result_list[i] = '增压反转2s'
    #             t_start = i
    #             state =4
    #         elif float(v_list[i]) >0 and float(v_list[i-1])==0 and float(v_list[i+1])>0 and float(i_list[i])>=i_thr:
    #             result_list[i] = '正转积分过流'
    #             t_start =i
    #             state=2
    #         elif float(v_list[i]) >0 and float(v_list[i-1])==0 and float(v_list[i+1])>0 and float(i_list[i]) <i_thr:
    #             result_list[i] = '正常运行'
    #             t_start = i
    #             state =1
    #     elif state ==4:
    #         result_list[i] = '增压反转2s'
    #         if float(v_list[i]) ==0 and float(v_list[i-1])<0 :
    #             result_list[i] = '停转'
    #             time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
    #             cnt_list[i-1] = cnt
    #             t_start = i
    #             state = 3
    #     elif state ==5:
    #         result_list[i] = '停止运行'

elif get_num2 == 2:
    state =0
# *********************************瞬时堵转分析*****************************************#
#                                                                                     #
#   state = 0 : 启动状态                                                                #
#   state = 1 : 瞬时堵转判定                                                             #
#   state = 2 : 反转2S                                                                 #
#   state = 3 : 反转3S                                                                 #
#   state = 4 : 停止运行                                                                #
#                                                                                     #
#*************************************************************************************#
    for i in range(0, len(i_list)):
        if state==  0 :
           if int(i_list[i]) == 0 or int(i_list[i]) ==1 or int(i_list[i])<0:
               result_list[i] = "未启动"
           elif int(i_list[i]) > 0 and int(i_list[i]) < i_thr:
               result_list[i] = "正常运行"
           elif int(i_list[i]) >=i_thr and int(i_list[i-1])< i_thr :
               result_list[i]= '瞬时堵转判定'
               t_start = i
               state=1
        elif state ==1:
            result_list[i] = '瞬时堵转判定'
            if int(i_list[i]) <i_thr :
                result_list[i] = ''
            if int(i_list[i]) < i_thr and int(i_list[i-1])>=i_thr:
                cnt= cnt +1
                time_statistic[i-1] = (total_time_list[i-1]-total_time_list[t_start])/1000
                cnt_list[i-1] = cnt
                flag = 1
            if float(v_list[i])<0 and float(v_list[i-1])>0:
                if flag == 0:
                    cnt=cnt+1
                    time_statistic[i-1] = (total_time_list[i-1]-total_time_list[t_start])/1000
                    cnt_list[i - 1] = cnt
                    flag = 0
                t_start = i
                if c == 0:
                    result_list[i] = '反转2s'
                    state =2
                else:
                    result_list[i] = '反转3s'
                    state =3
            elif float(v_list[i])==0 and float(v_list[i+1])==0 and float(v_list[i+2])==0:
                time_statistic[i-1] = (total_time_list[i-1]-total_time_list[t_start])/1000
                state=4
        elif state ==2:
            result_list[i] = '反转2s'
            if float(v_list[i])>0 and float(v_list[i-1])<0:
                time_statistic[i-1] = (total_time_list[i-1]-total_time_list[t_start])/1000
                cnt_list[i - 1] = cnt
                result_list[i] = '瞬时堵转判定'
                t_start =i
                state =1
                c=1
            elif float(v_list[i]) == 0 and float(v_list[i+1]) ==0:
                state = 4
        elif state ==3:
            result_list[i]= '反转3s'
            if float(v_list[i])>0 and float(v_list[i-1])<0:
                time_statistic[i-1] = (total_time_list[i-1]-total_time_list[t_start])/1000
                cnt_list[i-1] = cnt
                result_list[i] = '瞬时堵转判定'
                t_start =i
                state =1
                c=0
            elif float(v_list[i]) == 0 and float(v_list[i+1])==0:
                state = 4
        elif state == 4:
            result_list[i] = '停止运行'

# ************************************************************************************#
#                                                                                     #
#   state = 0 : 未启动                                                                 #
#   state = 1 : 正常运行                                                               #
#   state = 2 : 弱卡滞过流                                                             #
#   state = 3 : 停转                                                                  #
#   state = 4 : 反转2S                                                                #
#   state = 5 : 停止运行                                                               #
#                                                                                    #
#***********************************弱卡滞过流分析***************************************#
elif get_num2 ==3:
    state=0
    cnt=0
    t_start=0
    flag = 0
    c=0
    for i in range(0,len(i_list)):
        if state ==0:
            result_list[i] = '未启动'
            if int(i_list[i]) >0 and int(i_list[i]) <i_thr and int(i_list[i+1])>0:
                result_list[i] = '正常运行'
                t_start = i
                state = 1
        if state ==1:
            result_list[i] = '正常运行'
            if int(v_list[i]) ==0 and int(i_list[i-1]) >0 and int(v_list[i+1]) ==0:  #修改
                result_list[i] = '停转'
                t_start = i
                state = 3
            elif int(i_list[i]) >=i_thr and int(i_list[i-1]) <i_thr and int(i_list[i+1]) >=i_thr:
                result_list[i] = '弱卡滞过流'
                t_start = i
                state = 2
        elif state ==2:
            result_list[i] = '弱卡滞过流'
            if float(i_list[i]) <i_thr:
                result_list[i]= '未过流'
            elif float(i_list[i]) >= i_thr and float(i_list[i-1])<i_thr:
                t_start = i
            if float(v_list[i]) ==0 and float(v_list[i-1])>0 and float(v_list[i+1])>0:
                result_list[i] = '异常'
            elif float(v_list[i])==0 and float(v_list[i-1]) >0 and float(v_list[i+15]) ==0 and float(v_list[i+14]) ==0:
                result_list[i] = '停止运行'
                cnt=cnt+1
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i - 1] = cnt
                t_start = i
                state=5
            elif float(v_list[i]) <0:
                cnt=cnt+1
                result_list[i] = '反转2s'
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state=4
            elif (float(v_list[i])==0 and float(v_list[i-1]))>0 or ((float(v_list[i])==0 and float(v_list[i+1]))) <0 : #and float(v_list[i+1]) ==0 :
                cnt=cnt+1
                result_list[i] = '停转'
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state=3
        elif state ==3 :
            result_list[i] = '停转'
            if int(v_list[i]) <0 and int(v_list[i-1]) ==0 and int(v_list[i+1])<0:
                result_list[i] = '反转2s'
                t_start = i
                state =4
            elif float(v_list[i]) >0 and float(v_list[i-1])==0 and float(v_list[i+1])>0 and float(i_list[i])>=i_thr:
                result_list[i] = '弱卡滞过流'
                t_start =i
                state=2
            elif float(v_list[i]) >0 and float(v_list[i-1])==0 and float(v_list[i+1])>0 and float(i_list[i]) <i_thr:
                result_list[i] = '正常运行'
                t_start = i
                state =1
        elif state ==4:
            result_list[i] = '反转2s'
            if float(v_list[i])>0:
                result_list[i] = '弱卡滞过流'
                time_statistic[i - 1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state=2
            elif float(v_list[i]) ==0 and float(v_list[i-1])<0 :
                result_list[i] = '停转'
                time_statistic[i-1] = (total_time_list[i - 1] - total_time_list[t_start]) / 1000
                cnt_list[i-1] = cnt
                t_start = i
                state = 3
        elif state ==5:
            result_list[i] = '停止运行'
else :
    print('\n过流类型输入错误，请重新打开程序输入\n')

# with open('total_time_list.txt','w') as f_total_time :
#     for i in range(0,len(total_time_list)):
#         f_total_time.write(str(total_time_list[i])+'\n')
#
#   将每一行后面的\n 替换为 \t
for i in range(0,len(data_exc)):
    data_exc[i]=data_exc[i].replace('\n','\t')
# with open("result_list.txt",'w',encoding="utf-8") as f_result:
#     for i in range(0,len(result_list)):
#         f_result.write(data[i]+'\t'+result_list[i]+'\t'+str(cnt_list[i])+'\t'+str(time_statistic[i])+'\n')
# print(i_list)
# print(data[0])
# print(len(time_list))
# print((i_list))
# print(len(v_list))
# print(len(time_list))
# print(len(i_list))
# x = np.linspace(0, 10, 100)
# y = np.sin(x)
# x=[1,2,3]
# y=[4,5,6]
# plt.plot(x,y)
# x = np.linspace(0, 10, 30)
# plt.plot(x, np.sin(x))
# plt.show()
# with write('i_list.txt','w') as f:
#     f.writelines(i_list)
# ay = plt.gca()
# ay.yaxis.set_major_locator(MultipleLocator(10))

# with open('D:/projects/pycharm_project/i_data.txt','w') as f:
#     f.writelines(i_list[i])
# # 指定默认字体为支持中文的字体，例如 SimHei
# matplotlib.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
# matplotlib.rcParams['axes.unicode_minus'] = False # 解决保存图像时负号'-'显示为方块的问题



# # 创建一个图形
# plt.figure(figsize=(20, 6))

# # 绘制线图
# plt.plot(time_list, i_list,marker='o', label='电流', color='red', linewidth=2,ms='4')
# # plt.plot(time_list, v_list, marker='o',label='电压', color='blue', linewidth=2,ms='4', linestyle='--')

# plt.plot(time_list,v_list)
# plt.show()

# # 添加标题和标签
# plt.title('滚刷电机电流与电压')
# plt.xlabel('时间')
# plt.ylabel('Y轴')
# plt.legend() # 显示图例
# plt.grid(True) # 显示网格

# plt.show()
# print("\033[5;31;47m程序运行结束")
# print('\n'.join([''.join([('Love'[(x-y) % len('Love')] if ((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3 <= 0 else ' ') for x in range(-30, 30)]) for y in range(30, -30, -1)]))
# print('程序运行结束\033[0m')
# print("\033[5;31;47m程序运行结束")


# df= pd.read_csv('result_list.txt',delimiter='\t')
# df.to_excel('处理结果.xlsx',index=False)
#创建dataframe数据
data = {'原数据':data_exc,'状态':result_list,'时间':time_statistic,'计数':cnt_list,}
df = pd.DataFrame(data)
#生成excel表格
df.to_excel(f'{work_evr}{work_mode}_处理结果.xlsx',index=False)
# with open('result_list.txt', 'r') as file:
#     for line in file:
#         data.append(line.strip().split('\t'))
#
# # 写入Excel文件
# wb = workbook()
# ws = wb.active
# for row in data:
#     ws.append(row)
# wb.save('output.xlsx')


a = input('\n程序运行结束，工作辛苦了，输入回车结束：')

