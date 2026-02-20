import fnmatch
import re
import os
import pandas as pd
from collections import defaultdict

#print(f"📁 文件保存在: ./{OUTPUT_DIR}/")
#
print('📁*************************风机rpm异常阈值设置************************')
rpm_thr = int(input("\n请输入异常阈值:    "))
print(f'\n================异常阈值为：{rpm_thr}')

for f_name in os.listdir('.'):
    if fnmatch.fnmatch(f_name, '*.txt'):
        f= f_name
        # print(f_name)
pattern = r'(\w+\s+\d+\#)\.'
# print(f_name)
match = re.match(pattern,f)
# print(match.group(1))
file_name = match.group(1)
#打开txt文件并删除前4行和后20行
with open(f,'r', encoding='utf-8') as file:
    data_fan= file.readlines()

# print(data_exc)
    # del data_exc[0:4]
    # # del data_exc[-20:-1]
    # # del data_exc[-1]
    # del data_exc[-20:]

# print(type(data_exc))
# for i in range(0,len(data_exc)):
    # data_exc[i] = data_exc[i].replace('\n', '')
    # if data_exc[i] == '\n':
    #     del data_exc[i]
# print(data_exc)

def parse_list_to_dict(data_list):
    """
    将包含时间戳和变量数据的列表转换为字典
    """
    data_dict = defaultdict(list)
    for line in data_list:
        # # 匹配时间戳
        # timestamp_match = re.match(r'(\d{8}-\d{2}:\d{2}:\d{2}).*\*\*fan', line)
        # # print(timestamp_match)
        # if timestamp_match:
        #     timestamp = timestamp_match.group(1)
        #     # print(type(timestamp))
        #     data_dict['timestamp'].append(timestamp)
        # 匹配所有 **变量名 : 值 的模式
        # pattern = r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)'
        pattern = r'(\d{8}-\d{2}:\d{2}:\d{2}).*\*\*(fanRpm)\s*:\s*([^\s*]+)'
        matches = re.findall(pattern, line)
        # print(matches)
        for timestamp,variable_name, variable_value in matches:
            try:
                if '.' in variable_value:
                    variable_value = float(variable_value)
                else:
                    variable_value = int(variable_value)
            except ValueError:
                pass
            data_dict['timestamp'].append(timestamp)
            data_dict[variable_name].append(variable_value)
    return dict(data_dict)

temp_dict =parse_list_to_dict(data_fan)
total_time_list = temp_dict['timestamp']

fanrpm_list = temp_dict['fanRpm']

cnt=0
cnt1=0
cnt2 = 0
cnt3 = 0
cnt4=0
cnt5=0
cnt_fail=0
cnt_list    = []
time_list   = []
time1_list  = []
time2_list  = []
time3_list  = []
time4_list  = []
time5_list  = []
time_fail_list = []
value_list  =[]
value1_list = []
for i in range(0,len(fanrpm_list)):
    if fanrpm_list[i] ==0 and fanrpm_list[i+1]>0 and fanrpm_list[i+1] <=rpm_thr  :
        cnt=cnt+1
        time_list.append(total_time_list[i])
    if fanrpm_list[i] ==0 and fanrpm_list[i+1]>0 and fanrpm_list[i+1] <=rpm_thr  and fanrpm_list[i+2]>rpm_thr:
        cnt1 = cnt1 +1
        time1_list.append(total_time_list[i])
    if fanrpm_list[i] ==0 and fanrpm_list[i+1]>0 and fanrpm_list[i+1] <=rpm_thr and fanrpm_list[i+2]<=rpm_thr and \
       fanrpm_list[i+3]>rpm_thr:
        cnt2=cnt2+1
        time2_list.append(total_time_list[i])
    if fanrpm_list[i] == 0 and fanrpm_list[i + 1] > 0 and fanrpm_list[i + 1] <= rpm_thr and \
       fanrpm_list[i + 2] <= rpm_thr and fanrpm_list[i + 3] <= rpm_thr and fanrpm_list[i+4]>rpm_thr:
        cnt3=cnt3+1
        time3_list.append(total_time_list[i])
    if fanrpm_list[i] == 0 and fanrpm_list[i + 1] > 0 and fanrpm_list[i + 1] <= rpm_thr and \
       fanrpm_list[i + 2] <= rpm_thr and fanrpm_list[i + 3] <= rpm_thr and fanrpm_list[i + 4] <= rpm_thr and fanrpm_list[i+5]>rpm_thr:
        cnt4=cnt4+1
        time4_list.append(total_time_list[i])
    if fanrpm_list[i] == 0 and fanrpm_list[i + 1] > 0 and fanrpm_list[i + 1] <= rpm_thr and fanrpm_list[i + 2] <= rpm_thr\
       and fanrpm_list[i + 3] <= rpm_thr and fanrpm_list[i + 4] <= rpm_thr and fanrpm_list[i + 5] <= rpm_thr and fanrpm_list[i+6]>rpm_thr:
        cnt5=cnt5+1
        time5_list.append(total_time_list[i])
    if fanrpm_list[i] == 0 and fanrpm_list[i + 1] > 0 and fanrpm_list[i + 1] <= rpm_thr and fanrpm_list[i + 2] <= rpm_thr \
            and fanrpm_list[i + 3] <= rpm_thr and fanrpm_list[i + 4] <= rpm_thr and fanrpm_list[i + 5] <= rpm_thr and \
            fanrpm_list[i + 6] <= rpm_thr:
        cnt_fail = cnt_fail+1
        time_fail_list.append(total_time_list[i])


time1_list.insert(0,cnt1)
time2_list.insert(0,cnt2)
time3_list.insert(0,cnt3)
time4_list.insert(0,cnt4)
time5_list.insert(0,cnt5)
time_fail_list.insert(0,cnt_fail)


s1 = pd.Series(time1_list)
s2 = pd.Series(time2_list)
s3 = pd.Series(time3_list)
s4 = pd.Series(time4_list)
s5 = pd.Series(time5_list)
s6 = pd.Series(time_fail_list)
# print(s6)

# data={'次数':cnt_list,'时间':time1_list,'value1':value_list,'value2':value1_list}
# df = pd.DataFrame(data)
# df.to_excel(f'风机_处理结果.xlsx',index=False)
# data={'总时间':time_list,'一次时间':time1_list,'二次时间':time2_list,'三次时间':time3_list}
data = {'1s内启动':s1,'1.5s内启动':s2,'2s内启动':s3,'2.5s内启动':s4,'3s内启动':s5,'未成功启动':s6}
# print(data)
df = pd.DataFrame(data)
# df.fillna('NaN')
df.to_excel(f'{file_name}_处理结果.xlsx',index=False)
print(len(total_time_list))

# with open('time_list.txt','w') as f_i:
#     for i in range(0,len(time_list)):
#         f_i.write(time_list[i]+'\n')
#
# with open('time1_list.txt','w') as f_i:
#     for i in range(0,len(time1_list)):
#         f_i.write(time1_list[i]+'\n')
# with open('time2_list.txt','w') as f_i:
#     for i in range(0,len(time2_list)):
#         f_i.write(time2_list[i]+'\n')
# with open('time3_list.txt','w') as f_i:
#     for i in range(0,len(time3_list)):
#         f_i.write(time3_list[i]+'\n')
#
# with open('time4_list.txt','w') as f_i:
#     for i in range(0,len(time4_list)):
#         f_i.write(time4_list[i]+'\n')


# print(len(time_list))
# print(len(fanrpm_list))
# for key,value in temp_dict.items():
#     print(key)
# print(temp_dict)
# with open('C:/Users/dreame/Desktop/红外wifi压测/wifi.txt','r', encoding='utf-8') as file:
#     data_wifi = file.readlines()
