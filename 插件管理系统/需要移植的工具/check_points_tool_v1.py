import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading #线程
import time
import datetime
import xlsxwriter

import numpy as py
import pandas as pd
from pandas import DataFrame

import openpyxl
from pandas import DataFrame
# import xlsxwriter
from openpyxl.styles import Border, Side, Alignment, Font
from openpyxl import load_workbook, Workbook





class SerialTool:
    #初始化方法
    def __init__(self, root):

        #缓存变量
        self.num_temp       =0
        self.num_temp1      =0
        self.num_temp2      =0
        self.num_temp3      =0
        #编号变量
        self.num_batVolt    =0
        self.num_batCurrent =0
        self.num_imuAccX    =0
        self.num_imuAccY    =0
        self.num_imuAccZ    =0
        self.num_imuGryoX   =0
        self.num_imuGryoY   =0
        self.num_imuGryoZ   =0
        self.num_coorX      =0
        self.num_coorY      =0
        self.num_coorYaw    =0
        self.num_rolli      =0
        #缓存list
        self.temp_list          =[]
        """info -a 参数"""
        self.batVolt_list       =[]
        self.batCurrent_list    =[]
        self.imuAccX_list       =[]
        self.imuAccY_list       =[]
        self.imuAccZ_list       =[]
        self.imuGryoX_list      =[]
        self.imuGryoY_list      =[]
        self.imuGryoZ_list      =[]
        self.roll_list          =[]
        self.pitch_list         =[]
        self.yaw_list           =[]
        self.rollI_on_list      =[]
        self.rollI_off_list     =[]
        self.SOCEkfSend_list    =[]
        self.leftVel_r_list     =[]
        self.rightVel_r_list    =[]
        self.leftVel_f_list     =[]
        self.rightVel_f_list    =[]
        self.rightVel_stop_list =[]
        self.leftVel_stop_list  =[]
        self.leftI_f_list       =[]
        self.rightI_f_list      =[]
        self.leftI_off_list     =[]
        self.rightI_off_list    =[]
        self.mopLI_on_list      =[]
        self.mopRI_on_list      =[]
        self.mopLI_off_list     =[]
        self.mopRI_off_list     =[]
        self.mopSideI_ext_list      =[]
        self.mopSideI_int_list      =[]
        self.mopSideI_ext_off_list  =[]
        self.rollLiftI_on_list      =[]
        self.rollLiftI_off_list     =[]
        self.rollAngle_down_list    =[]
        self.rollAngle_up_list      =[]
        self.sideOutI_ext_list      =[]
        self.sideOutI_int_list      =[]
        self.sideOutI_ext_off_list  =[]
        self.fanRpm_on_list         =[]
        self.fanRpm_off_list        =[]
        self.fanCurrent_on_list     =[]
        self.fanCurrent_off_list    =[]
        self.CrossLI_1_list         =[]
        self.CrossLI_0_list         =[]
        self.CrossRI_1_list         =[]
        self.CrossRI_0_list         =[]
        self.CrossLVoltCtrl_1_list  =[]
        self.CrossLVoltCtrl_0_list  =[]
        self.CrossRVoltCtrl_1_list  =[]
        self.CrossRVoltCtrl_0_list  =[]
        self.sideI_on_list          =[]
        self.sideI_off_list         =[]
        self.liftChassisUniversalI_on_list   =[]
        self.liftChassisUniversalI_off_list  =[]
        self.scraperLiftI_on_list   =[]
        self.scraperLiftI_off_list  =[]
        self.echo1_list             =[]
        self.echo2_list             =[]
        self.echo3_list             =[]
        """io -h参数"""
        self.mopUp_left_1_list    =[]
        self.mopUp_right_1_list   =[]
        self.mopUp_left_0_list    =[]
        self.mopUp_right_0_list   =[]
        self.mopside_in_1_list    =[]
        self.mopside_in_0_list    =[]
        self.roll_lift_1_list     =[]
        self.roll_lift_0_list     =[]
        self.sideAdduction_1_list =[]
        self.sideAdduction_0_list =[]
        self.wheellift_up_1_list  =[]
        self.wheellift_up_0_list  =[]
        self.scraper_front_1_list =[]
        self.scraper_front_0_list =[]


        #计数
        self.cnt = 1
        self.wheellift_cnt = 1

        #接收数据控制信号
        self.receive_flag = 0

        #参数字典,用来存放info -a机器发送回的变量名与对应的编号
        self.para_dict = {}

        #存放变量前对应的编号
        self.number_list        = []

        #存放变量名
        self.var_list           = []
        #
        self.para_list          = []
        #关闭内部输入命令，打开外部输入命令
        self.flag_inside_cmd    = 0
        self.root = root   #root为对象
        self.root.title("点检自动化工具")   #title（）是Tk类中的一个方法
        self.root.geometry("800x600")       #geometry()也是Tk类中的一个方法
        
        # 串口对象
        self.ser = None                     #定义一个变量用来实现串口功能SerialTool类初始化方法中的属性
        self.is_connected = False           #同上

        # 创建界面
        self.create_widgets()           #调用类中的方法
    def create_widgets(self):
        # 串口配置区域
        config_frame = ttk.LabelFrame(self.root, text="串口配置", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # 端口选择
        ttk.Label(config_frame, text="端口:").grid(row=0, column=0, sticky="w")
        self.port_var = tk.StringVar(value="COM7")
        self.port_combo = ttk.Combobox(config_frame, textvariable=self.port_var, width=10)
        self.port_combo.grid(row=0, column=1, padx=5)
        
        # 波特率选择
        ttk.Label(config_frame, text="波特率:").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.baud_var = tk.StringVar(value="115200")
        self.baud_combo = ttk.Combobox(config_frame, textvariable=self.baud_var, width=10)
        self.baud_combo['values'] = ('9600', '19200', '38400', '57600', '115200')
        self.baud_combo.grid(row=0, column=3, padx=5)
        
        # 超时设置
        ttk.Label(config_frame, text="超时(秒):").grid(row=0, column=4, sticky="w", padx=(20,0))
        self.timeout_var = tk.StringVar(value="0.5")
        self.timeout_entry = ttk.Entry(config_frame, textvariable=self.timeout_var, width=10)
        self.timeout_entry.grid(row=0, column=5, padx=5)
        
        # 连接按钮
        self.connect_btn = ttk.Button(config_frame, text="连接", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=6, padx=(20,0))
        
        # 刷新端口按钮
        ttk.Button(config_frame, text="刷新端口", command=self.refresh_ports).grid(row=0, column=7, padx=5)

        # ttk.Button(config_frame, text="参数提取", command=self.para_extr).grid(row=1, column=2, padx=5) #新添加
        # ttk.Button(config_frame, text="一键处理", command=self.auto_exc).grid(row=1, column=3, padx=5) #新添加
        # ttk.Button(config_frame, text="停止接收", command=self.stop_receive).grid(row=1, column=4, padx=5) #新添加
        # ttk.Button(config_frame, text="屏蔽核心板", command=self.close_core).grid(row=1, column=5, padx=5) #新添加
        # ttk.Button(config_frame, text="恢复核心板", command=self.open_core).grid(row=1, column=6, padx=5) #新添加


        # 快捷命令区域
        hotkeys_frame = ttk.LabelFrame(self.root, text="快捷命令", padding=10)
        hotkeys_frame.pack(side='top', fill="x", padx=10, pady=5)

        ttk.Button(hotkeys_frame, text="参数提取", command=self.para_extr).grid(row=1, column=2, padx=5)
        self.button1=ttk.Button(hotkeys_frame, text="一键处理", command=self.auto_exc)
        self.button1.grid(row=1, column=3, padx=5)
        ttk.Button(hotkeys_frame, text="停止接收", command=self.stop_receive).grid(row=1, column=4, padx=5)
        ttk.Button(hotkeys_frame, text="屏蔽核心板", command=self.close_core).grid(row=1, column=5, padx=5)
        ttk.Button(hotkeys_frame, text="恢复核心板", command=self.open_core).grid(row=1, column=6, padx=5)


        # 发送指令区域
        send_frame = ttk.LabelFrame(self.root, text="发送指令", padding=10)
        send_frame.pack(fill="x", padx=10, pady=5)
        
        self.cmd_entry = ttk.Entry(send_frame)
        self.cmd_entry.pack(fill="x", side="left", expand=True)
        self.cmd_entry.bind("<Return>", lambda e: self.send_command())
        
        ttk.Button(send_frame, text="发送", command=self.send_command).pack(side="right", padx=(5,0))
        
        # 接收区域
        recv_frame = ttk.LabelFrame(self.root, text="接收数据", padding=10)
        recv_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.recv_text = scrolledtext.ScrolledText(recv_frame, height=15)
        self.recv_text.pack(fill="both", expand=True)
        
        # 控制按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="清空接收区", command=self.clear_receive).pack(side="left")
        ttk.Button(btn_frame, text="保存数据", command=self.save_data).pack(side="left", padx=5)
        
        # 初始化端口列表
        self.refresh_ports()
        
    def refresh_ports(self):
        """刷新可用串口列表"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
        print('刷新串口列表')

    def toggle_connection(self):
        """连接或断开串口"""
        if not self.is_connected:
            self.connect_serial()
        else:
            self.disconnect_serial()
    
    def connect_serial(self):
        """连接串口"""
        try:
            port = self.port_var.get()
            baudrate = int(self.baud_var.get())
            timeout = float(self.timeout_var.get())
            
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            self.is_connected = True
            self.connect_btn.config(text="断开")
            self.port_combo.config(state="disabled")
            self.baud_combo.config(state="disabled")
            self.timeout_entry.config(state="disabled")
            
            # 启动显示线程
            # self.append_receive_thread = threading.Thread(target=self.append_receive,args=('hello',),daemon=True)
            # self.append_receive_thread.start()
            # #启动发送命令线程
            # self.send_command_thread = threading.Thread(target=self.send_command,daemon=True)
            # self.send_command_thread.start()
            #启动接收数据线程
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
            # self.receive_thread.setDaemon(True)
            self.receive_thread.start()
            self.loop_send_thread = threading.Thread(target=self.loop_send, daemon=True)

            #启动接收线程
            # self.receive_pro = Process(target=self.receive_data)
            # self.receive_pro.start()
            # self.receive_pro.join()
            self.append_receive(f"已连接到 {port}，波特率 {baudrate}\n")
            
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接串口: {str(e)}")
    
    def disconnect_serial(self):
        """断开串口连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False
        self.connect_btn.config(text="连接")
        self.port_combo.config(state="readonly")
        self.baud_combo.config(state="readonly")
        self.timeout_entry.config(state="normal")
        self.append_receive("已断开串口连接\n")

    def close_core(self):
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接串口")
            return
        self.flag_inside_cmd =1
        self.cmd = 'core -S'
        self.send_command()
        self.flag_inside_cmd = 0

    def open_core(self):
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接串口")
            return
        self.flag_inside_cmd =1
        self.cmd = 'core -R'
        self.send_command()
        self.flag_inside_cmd = 0

    def stop_receive(self):
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接串口")
            return
        self.flag_inside_cmd =1
        self.cmd = '\\'
        self.send_command()
        self.flag_inside_cmd = 0

    def para_extr(self):
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接串口")
            return
        # pass
        self.flag_inside_cmd=1
        self.cmd = '<QUIT>'
        self.send_command()
        time.sleep(0.1)
        self.cmd = 'info -a'
        self.send_command()
        self.flag_inside_cmd = 0


    #启动loop_send线程
    def auto_exc(self):
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接串口")
            return

        # self.receive_thread.start()
        self.loop_send_thread.start()

    #提取变量名对应的参数的方法
    def arg_extr(self,temp_list=[],var_name=''):
        l = len(var_name)
        result_list = []
        for i in range(0,len(temp_list)):
            for j in range(0,len(temp_list[i])):
                if temp_list[i][j:j+l] == var_name and self.temp_list[i][j:j+16].strip()==var_name:
                    result_list.append(int(temp_list[i][j+17:j+24].strip()))
        return result_list

    #main_execute
    def loop_send(self):

        # if not self.is_connected:
        #     messagebox.showwarning("未连接", "请先连接串口")
        #     return

        self.button1['state'] = 'disabled'
        #屏蔽核心板
        self.flag_inside_cmd = 1
        print('关闭外部输入命令')
        self.cmd = 'core -S'
        self.send_command()
        time.sleep(1)
        #进入Xshell
        self.cmd = '<QUIT>'
        self.send_command()
        time.sleep(1)
        #获取参数列表
        self.cmd= 'info -a'
        self.temp_list.clear()
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        time.sleep(7)
        self.receive_flag = 0
        # print('命令发送完成')
        time.sleep(1)
        # print(self.temp_list)
        self.cmd = 'core -S'
        self.send_command()
        time.sleep(1)
        #标定
        self.cmd = 'state /caliVI'
        self.send_command()
        time.sleep(1)

        self.para_list = self.temp_list
        #提取var
        for i in range(0,len(self.para_list)):
            # print(self.para_list[i])
            for j in range(0,len(self.para_list[i])):
                if self.para_list[i][j:j+3] == 'Var':
                    start = j+4
                if self.para_list[i][j:j+3] == 'Att':
                    end = j
                    self.var_list.append(self.para_list[i][start:end].strip())
        print(self.var_list)
        # return

        #生成字典的value，num
        for i in range(0,len(self.var_list)):
            self.number_list.append(i+1)
        print(self.number_list)
        #创建参数字典  dict{var_list,num_list}
        self.para_dict = dict(zip(self.var_list,self.number_list))
        #查找字典，找到变量对应的编号
        self.num_batVolt    =      self.para_dict.get('batVolt(mV)')  #或者用self.para_dict['batVolt(mV)'],但是这个如果查找不到键值会报错
        self.num_batCurrent =      self.para_dict.get('batCurrent')
        self.num_imuAccX    =      self.para_dict.get('imuAccX')
        self.num_imuAccY    =      self.para_dict.get('imuAccY')
        self.num_imuAccZ    =      self.para_dict.get('imuAccZ')
        self.num_imuGryoX   =      self.para_dict.get('imuGryoX')
        self.num_imuGryoY   =      self.para_dict.get('imuGryoY')
        self.num_imuGryoZ   =      self.para_dict.get('imuGryoZ')
        self.num_roll       =      self.para_dict.get('roll')
        self.num_pitch      =      self.para_dict.get('pitch')
        self.num_Yaw        =      self.para_dict.get('yaw')
        self.num_rollI      =      self.para_dict.get('rollI(mA)')

        self.cmd = f'mon -m50 /{self.num_batVolt}/{self.num_batCurrent}/{self.num_imuAccX}/' \
                   f'{self.num_imuAccY}/{self.num_imuAccZ}/{self.num_imuGryoX}/{self.num_imuGryoY}/' \
                   f'{self.num_imuGryoZ}/{self.num_roll}/{self.num_pitch}/{self.num_Yaw }'

        self.temp_list.clear()#每次使用temp_list前先清空
        self.receive_flag =1
        self.send_command()
        time.sleep(3)
        self.receive_flag =0
        self.cmd = '\\'
        # print(self.first_list)
        self.send_command()
        #发送完停止命令之后再处理数据，保证数据接收完成
        # self.temp_list.clear()              #清空temp_list
        time.sleep(1)

        #调用参数提取方法
        self.batVolt_list       = self.arg_extr(self.temp_list,'batVolt(mV)')
        self.batCurrent_list    = self.arg_extr(self.temp_list,'batCurrent')
        self.imuAccX_list       = self.arg_extr(self.temp_list,'imuAccX')
        self.imuAccY_list       = self.arg_extr(self.temp_list,'imuAccY')
        self.imuAccZ_list       = self.arg_extr(self.temp_list,'imuAccZ')
        self.imuGryoX_list      = self.arg_extr(self.temp_list,'imuGryoX')
        self.imuGryoY_list      = self.arg_extr(self.temp_list,'imuGryoY')
        self.imuGryoZ_list      = self.arg_extr(self.temp_list,'imuGryoZ')
        self.roll_list          = self.arg_extr(self.temp_list,'roll')
        self.pitch_list         = self.arg_extr(self.temp_list,'pitch')
        self.yaw_list           = self.arg_extr(self.temp_list,'yaw')

        print(f'电池电压为：{self.batVolt_list}')
        print(f'电池电流为：{self.batCurrent_list}')
        print(f'imu加速度X轴为：{self.imuAccX_list}')
        print(f'imu加速度Y轴为：{self.imuAccY_list}')
        print(f'imu加速度Z轴为：{self.imuAccZ_list}')
        print(f'imu陀螺仪X轴为：{self.imuGryoX_list}')
        print(f'imu陀螺仪Y轴为：{self.imuGryoY_list}')
        print(f'imu陀螺仪Z轴为：{self.imuGryoZ_list}')
        print(f'偏航角为：{self.yaw_list}')
        print(f'横滚角为：{self.roll_list}')
        print(f'俯仰角为：{self.pitch_list}')
        # return

        #滚刷电机电流-打开/关闭

        time.sleep(3)
        self.temp_list.clear()              #清空temp_list
        self.cmd = f'mon -m50 /{self.num_rollI}'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  #标志为开启之前清楚temp_list
        self.cmd = 'roll 10500'
        self.receive_flag =1
        time.sleep(0.2)
        self.send_command()
        time.sleep(3)
        self.receive_flag =0
        self.rollI_on_list = self.arg_extr(self.temp_list,'rollI(mA)')  #调用提取参数方法
        print(f'滚刷电机电流-打开：{self.rollI_on_list}')
        time.sleep(1)
        self.temp_list.clear()
        self.cmd = 'roll 0'
        self.send_command()
        time.sleep(2)
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        self.rollI_off_list = self.arg_extr(self.temp_list,'rollI(mA)')
        print(f'滚刷电机电流-关闭：{self.rollI_off_list}')
        self.temp_list.clear()
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #电量检测
        self.num_temp = self.para_dict.get('SOCEkfSend')
        self.cmd = f'mon -m50 /{self.num_temp}'
        self.send_command()
        time.sleep(3)
        self.temp_list.clear()  #标志位开启之前清楚temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        self.SOCEkfSend_list = self.arg_extr(self.temp_list,'SOCEkfSend')
        print(f'SOCEkfSend为：{self.SOCEkfSend_list}')
        self.temp_list.clear()
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #左右轮转速-空载正转
        self.num_temp = self.para_dict.get('leftVel')
        self.num_temp1= self.para_dict.get('rightVel')
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'move -lr 300 300'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  #标志位开启之前清楚temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.leftVel_f_list = self.arg_extr(self.temp_list,'leftVel')
        self.rightVel_f_list = self.arg_extr(self.temp_list,'rightVel')
        print(f'左轮转速-空载正转为：{self.leftVel_f_list}')
        print(f'右轮转速-空载正转为：{self.rightVel_f_list}')
        self.temp_list.clear()
        self.cmd = 'move -lr 0 0'
        self.send_command()
        time.sleep(2)
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #左右轮转速-空载反转
        self.num_temp = self.para_dict.get('leftVel')
        self.num_temp1 = self.para_dict.get('rightVel')
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'move -lr -300 -300'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.leftVel_r_list = self.arg_extr(self.temp_list, 'leftVel')
        self.rightVel_r_list = self.arg_extr(self.temp_list, 'rightVel')
        print(f'左轮转速-空载反转为：{self.leftVel_r_list}')
        print(f'右轮转速-空载反转为：{self.rightVel_r_list}')
        self.temp_list.clear()
        self.cmd = 'move -lr 0 0'
        self.send_command()
        time.sleep(3)
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.leftVel_stop_list = self.arg_extr(self.temp_list, 'leftVel')
        self.rightVel_stop_list = self.arg_extr(self.temp_list, 'rightVel')
        print(f'左轮转速-停转为：{self.leftVel_stop_list}')
        print(f'右轮转速-停转为：{self.rightVel_stop_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #左右轮电流-空载正转
        self.num_temp = self.para_dict.get('leftI(mA)')
        self.num_temp1 = self.para_dict.get('rightI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'move -lr -300 -300'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.leftI_f_list = self.arg_extr(self.temp_list, 'leftI(mA)')
        self.rightI_f_list = self.arg_extr(self.temp_list, 'rightI(mA)')
        print(f'左轮电流-空载正转为：{self.leftI_f_list}')
        print(f'右轮电流-空载正转为：{self.rightI_f_list}')
        self.temp_list.clear()
        self.cmd = 'move -lr 0 0'
        self.send_command()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #左右轮电流-关闭
        self.num_temp = self.para_dict.get('leftI(mA)')
        self.num_temp1 = self.para_dict.get('rightI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'move -lr 0 0'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.leftI_off_list = self.arg_extr(self.temp_list, 'leftI(mA)')
        self.rightI_off_list = self.arg_extr(self.temp_list, 'rightI(mA)')
        print(f'左轮电流-关闭为：{self.leftI_off_list}')
        print(f'右轮电流-关闭为：{self.rightI_off_list}')
        self.temp_list.clear()
        self.cmd = 'move -lr 0 0'
        self.send_command()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #左右抹布电流-开启
        self.num_temp = self.para_dict.get('mopLI(mA)')
        self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'mop -lr 12000'
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(0.3)
        self.send_command()
        time.sleep(4)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        # time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.mopLI_on_list = self.arg_extr(self.temp_list, 'mopLI(mA)')
        self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'左抹布电流-开启为：{self.mopLI_on_list}')
        print(f'右抹布电流-开启为：{self.mopRI_on_list}')
        self.temp_list.clear()

        #左右抹布电流关闭
        self.cmd = 'mop -lr 0'
        time.sleep(0.3)
        self.send_command()
        time.sleep(5)
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag =0
        print(self.temp_list)
        self.mopLI_off_list = self.arg_extr(self.temp_list, 'mopLI(mA)')
        self.mopRI_off_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'左抹布电流-关闭为：{self.mopLI_off_list}')
        print(f'右抹布电流-关闭为：{self.mopRI_off_list}')
        self.temp_list.clear()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()

        #抹布外扩电流
        self.num_temp = self.para_dict.get('mopSideI(mA)')
        # self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'mopside 8000'
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # time.sleep(1.5)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.mopSideI_ext_list = self.arg_extr(self.temp_list, 'mopSideI(mA)')
        print(f'抹布外扩电流mopSideI为：{self.mopSideI_ext_list}')
        self.temp_list.clear()
        #抹布内收电流
        self.cmd = 'mopside -8000'
        # time.sleep()
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # time.sleep(1.6)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.mopSideI_int_list = self.arg_extr(self.temp_list, 'mopSideI(mA)')
        print(f'抹布内收电流mopSideI为：{self.mopSideI_int_list}')
        self.temp_list.clear()
        time.sleep(2)
        # 抹布外扩电流关闭
        self.temp_list.clear()
        self.cmd = 'mopside 0'
        self.send_command()
        time.sleep(2)
        self.temp_list.clear()
        self.receive_flag = 1
        time.sleep(2)
        self.receive_flag = 0
        print(self.temp_list)
        self.mopSideI_ext_off_list = self.arg_extr(self.temp_list, 'mopSideI(mA)')
        print(f'抹布外扩关闭电流mopSideI为：{self.mopSideI_ext_off_list}')
        self.temp_list.clear()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)


        # #滚刷升降电机电流 -打开
        self.num_temp = self.para_dict.get('rollLiftI')
        self.cmd = f'mon -m50 /{self.num_temp}'
        self.send_command()
        time.sleep(1)
        self.cmd = 'rolllift -1'
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # time.sleep(0.2)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.rollLiftI_on_list = self.arg_extr(self.temp_list, 'rollLiftI')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'滚刷升降电机电流-开启：{self.rollLiftI_on_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        #滚刷升降电机电流-关闭
        self.cmd = 'rolllift -0'
        self.send_command()
        time.sleep(0.2)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.rollLiftI_off_list = self.arg_extr(self.temp_list, 'rollLiftI')
        print(f'滚刷升降电机电流-关闭：{self.rollLiftI_off_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #滚刷电机角度-下降
        self.num_temp = self.para_dict.get('rollAngle')
        # self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'rolllift -1'
        self.send_command()
        time.sleep(5)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.rollAngle_down_list = self.arg_extr(self.temp_list, 'rollAngle')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'滚刷电机角度-下降：{self.rollAngle_down_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        #滚刷电机角度-抬升
        self.cmd = 'rolllift -0'
        self.send_command()
        time.sleep(5)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.rollAngle_up_list = self.arg_extr(self.temp_list, 'rollAngle')
        print(f'滚刷电机角度-抬升：{self.rollAngle_up_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #边刷外扩电流
        self.num_temp = self.para_dict.get('sideOutI(mA)')
        # self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'sideout 8000'
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # time.sleep(1.5)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.sideOutI_ext_list = self.arg_extr(self.temp_list, 'sideOutI(mA)')
        # self.mopRI_off_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'边刷外扩电流sideOutI(mA)为：{self.sideOutI_ext_list}')
        # print(f'右抹布关闭mopRI为：{self.mopRI_off_list}')
        #边刷内收电流
        self.cmd = 'sideout -8000'
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # time.sleep(0.3)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.sideOutI_int_list = self.arg_extr(self.temp_list, 'sideOutI(mA)')
        print(f'边刷内收电流sideOutI(mA)为：{self.sideOutI_int_list}')
        self.temp_list.clear()
        time.sleep(2)
        # 边刷外扩电流关闭
        self.temp_list.clear()
        self.cmd = 'sideout 0'
        self.send_command()
        time.sleep(2)
        self.temp_list.clear()
        self.receive_flag = 1
        time.sleep(2)
        self.receive_flag = 0
        print(self.temp_list)
        self.sideOutI_ext_off_list = self.arg_extr(self.temp_list, 'sideOutI(mA)')
        print(f'边刷外扩关闭电流sideOutI(mA)为：{self.sideOutI_ext_off_list}')
        self.temp_list.clear()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)


        #风机转速-开启
        self.num_temp = self.para_dict.get('fanRpm')
        # self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'fan 300'
        self.send_command()
        time.sleep(5)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.fanRpm_on_list = self.arg_extr(self.temp_list, 'fanRpm')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'风机转速-开启：{self.fanRpm_on_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        #风机转速-关闭
        self.cmd = 'fan 0'
        self.send_command()
        time.sleep(4)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.fanRpm_off_list = self.arg_extr(self.temp_list, 'fanRpm')
        print(f'风机转速-关闭：{self.fanRpm_off_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #风机电流-开启
        self.num_temp = self.para_dict.get('fanCurrent')
        # self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(3)
        self.cmd = 'fan 300'
        self.send_command()
        time.sleep(3)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.fanCurrent_on_list = self.arg_extr(self.temp_list, 'fanCurrent')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'风机电流-开启：{self.fanCurrent_on_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        #风机电流-关闭
        self.cmd = 'fan 0'
        self.send_command()
        time.sleep(3)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0
        print(self.temp_list)
        self.fanCurrent_off_list = self.arg_extr(self.temp_list, 'fanCurrent')
        print(f'风机电流-关闭：{self.fanCurrent_off_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #越障电机打开
        self.num_temp = self.para_dict.get('CrossLI(mA)')
        self.num_temp1 = self.para_dict.get('CrossRI(mA)')
        self.num_temp2 = self.para_dict.get('CrossLVoltCtrl')
        self.num_temp3 = self.para_dict.get('CrossRVoltCtrl')
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}/{self.num_temp2}/{self.num_temp3}'
        # print(self.num_temp)
        self.send_command()
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.cmd = 'cross -p 1'
        self.send_command()
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.CrossLI_1_list = self.arg_extr(self.temp_list, 'CrossLI(mA)')
        self.CrossRI_1_list = self.arg_extr(self.temp_list, 'CrossRI(mA)')
        self.CrossLVoltCtrl_1_list = self.arg_extr(self.temp_list, 'CrossLVoltCtrl')
        self.CrossRVoltCtrl_1_list = self.arg_extr(self.temp_list, 'CrossRVoltCtrl')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'左越障电机电流-到1：{self.CrossLI_1_list}')
        print(f'右越障电机电流-到1：{self.CrossRI_1_list}')
        print(f'左越障电机电压-到1：{self.CrossLVoltCtrl_1_list}')
        print(f'右越障电机电压-到1：{self.CrossRVoltCtrl_1_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(1)

        #越障电机关闭
        self.cmd = f'mon -m50 /{self.num_temp}/{self.num_temp1}/{self.num_temp2}/{self.num_temp3}'
        # print(self.num_temp)
        self.send_command()
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.cmd = 'cross -p 0'
        self.send_command()
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.CrossLI_0_list = self.arg_extr(self.temp_list, 'CrossLI(mA)')
        self.CrossRI_0_list = self.arg_extr(self.temp_list, 'CrossRI(mA)')
        self.CrossLVoltCtrl_0_list = self.arg_extr(self.temp_list, 'CrossLVoltCtrl')
        self.CrossRVoltCtrl_0_list = self.arg_extr(self.temp_list, 'CrossRVoltCtrl')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'左越障电机电流-到0：{self.CrossLI_0_list}')
        print(f'右越障电机电流-到0：{self.CrossRI_0_list}')
        print(f'左越障电机电压-到0：{self.CrossLVoltCtrl_0_list}')
        print(f'右越障电机电压-到0：{self.CrossRVoltCtrl_0_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)


        # 边刷电机电流-开启
        self.num_temp = self.para_dict.get('sideI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        self.send_command()
        time.sleep(1)
        self.cmd = 'side 8000'
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # time.sleep(3)
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.sideI_on_list = self.arg_extr(self.temp_list, 'sideI(mA)')
        print(f'边刷电机电流-开启：{self.sideI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        # 边刷电机电流-关闭
        self.cmd = 'side 0'
        self.send_command()
        time.sleep(3)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.sideI_off_list = self.arg_extr(self.temp_list, 'sideI(mA)')
        print(f'边刷电机电流-关闭：{self.sideI_off_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(3)

        # 万向轮电流-开启11mm
        self.num_temp = self.para_dict.get('liftChassisUniversalI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.cmd = 'wheellift -su 4'
        self.receive_flag = 1
        time.sleep(0.3)
        self.send_command()
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        for i in range(0,len(self.temp_list)):
            for j in range(0,len(self.temp_list[i])):
                if self.temp_list[i][j:j+len('liftChassisUniversalI(mA)')] == 'liftChassisUniversalI(mA)' :
                    self.liftChassisUniversalI_on_list.append(int(self.temp_list[i][j+1+len('liftChassisUniversalI(mA)'):j+5+len('liftChassisUniversalI(mA)')].strip()))
        print(f'万向轮电流-开启11mm：{self.liftChassisUniversalI_on_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        # 万向轮电流-关闭0mm
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.cmd = 'wheellift -su 0'
        self.receive_flag = 1
        time.sleep(0.3)
        self.send_command()
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)

        for i in range(0,len(self.temp_list)):
            for j in range(0,len(self.temp_list[i])):
                if self.temp_list[i][j:j+len('liftChassisUniversalI(mA)')] == 'liftChassisUniversalI(mA)' :
                    self.liftChassisUniversalI_off_list.append(int(self.temp_list[i][j+1+len('liftChassisUniversalI(mA)'):j+5+len('liftChassisUniversalI(mA)')].strip()))

        print(f'万向轮电流-关闭0mm：{self.liftChassisUniversalI_off_list}')
        self.temp_list.clear()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        # 刮条电机电流-开启
        self.num_temp = self.para_dict.get('scraperLiftI(mA)')
        # self.num_temp1 = self.para_dict.get('mopRI(mA)')
        self.cmd = f'mon -m50 /{self.num_temp}'
        # print(self.num_temp)
        self.send_command()
        time.sleep(1)
        self.cmd = 'scraperlift -p 2'
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.scraperLiftI_on_list = self.arg_extr(self.temp_list, 'scraperLiftI(mA)')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'刮条电机电流-开启：{self.scraperLiftI_on_list}')
        # print(f'右抹布mopRI为：{self.mopRI_on_list}')
        self.temp_list.clear()
        time.sleep(1)
        # 刮条电机电流-关闭
        self.cmd = 'scraperlift -p 0'
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(0.2)
        self.send_command()
        # self.temp_list.clear()  # 标志位开启之前清除temp_list
        # self.receive_flag = 1
        time.sleep(4)
        self.receive_flag = 0
        print(self.temp_list)
        self.scraperLiftI_off_list = self.arg_extr(self.temp_list, 'scraperLiftI(mA)')
        print(f'刮条电机电流-关闭：{self.scraperLiftI_off_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        #超声波回波
        self.cmd = 'ultra'
        self.send_command()
        time.sleep(1)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(1)
        self.receive_flag = 0
        print(self.temp_list)
        self.echo1_list = self.echo_extr(self.temp_list, 'echo1')
        self.echo2_list = self.echo_extr(self.temp_list, 'echo2')
        self.echo3_list = self.echo_extr(self.temp_list, 'echo3')
        # self.mopRI_on_list = self.arg_extr(self.temp_list, 'mopRI(mA)')
        print(f'echo1为：{self.echo1_list}')
        print(f'echo2为：{self.echo2_list}')
        print(f'echo3为：{self.echo3_list}')
        self.temp_list.clear()
        time.sleep(1)
        self.cmd = '\\'
        self.send_command()
        time.sleep(2)

        # io -h
        """  左-右 抹布抬升  """
        self.cmd = 'mop -lrd -5000'
        self.send_command()
        time.sleep(1)
        """ 抹布内收 """
        self.cmd = 'mopside -8000'
        self.send_command()
        time.sleep(2)

        """ 滚刷下降 """
        self.cmd = 'rolllift -1'
        self.send_command()
        time.sleep(2)

        """ 边刷内收 """
        self.cmd = 'sideout -8000'
        self.send_command()
        time.sleep(2)

        """ 万向轮5mm """
        self.cmd = 'wheellift -su 2'
        self.send_command()
        time.sleep(2)

        """ 刮条抬升 """
        self.cmd = 'scraperlift -p 0'
        self.send_command()
        time.sleep(2)

        self.cmd = 'io -h'
        self.send_command()
        time.sleep(0.2)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0

        # io -h参数提取
        print(self.temp_list)
        for i in range(0,len(self.temp_list)):
            for j in range(0,len(self.temp_list[i])):
                if self.temp_list[i][j:j+10] == 'mopUp-left':
                    self.mopUp_left_1_list.append(int(self.temp_list[i][j+11:j+13].strip()))
                    self.mopUp_right_1_list.append(int(self.temp_list[i][j+19:j+21].strip()))
                elif self.temp_list[i][j:j+11] == 'mopside-out':
                    self.mopside_in_1_list.append(int(self.temp_list[i][j+17:j+19].strip()))
                elif self.temp_list[i][j:j+9] == 'roll_lift':
                    self.roll_lift_1_list.append(int(self.temp_list[i][j+10:j+12].strip()))
                elif self.temp_list[i][j:j+13] == 'sideAdduction':
                    self.sideAdduction_1_list.append(int(self.temp_list[i][j+14:j+16].strip()))
                elif self.temp_list[i][j:j+9] == 'wheellift':
                    self.wheellift_up_1_list.append(int(self.temp_list[i][j+15:j+17].strip()))
                elif self.temp_list[i][j:j+13] == 'scraper front':
                    self.scraper_front_1_list.append(int(self.temp_list[i][j+14:j+16].strip()))

        print(f'mopUp_left_1_list为：{self.mopUp_left_1_list}')
        print(f'mopUp_right_1_list为：{self.mopUp_right_1_list}')
        print(f'mopside_in_1_list为：{self.mopside_in_1_list}')
        print(f'roll_lift_1_list为：{self.roll_lift_1_list}')
        print(f'sideAdduction_1_list为：{self.sideAdduction_1_list}')
        print(f'wheellift_up_1_list为：{self.wheellift_up_1_list}')
        print(f'scraper_front_1_list为：{self.scraper_front_1_list}')

        self.temp_list.clear()
        self.cmd = '\\'
        self.send_command()
        time.sleep(8)

        """  左-右 抹布抬升  """
        self.cmd = 'mop -lrd 5000'
        self.send_command()
        time.sleep(1)
        """ 抹布外扩 """
        self.cmd = 'mopside 8000'
        self.send_command()
        time.sleep(1)

        """ 滚刷抬升 """
        self.cmd = 'rolllift -0'
        self.send_command()
        time.sleep(1)

        """ 边刷外扩 """
        self.cmd = 'sideout 8000'
        self.send_command()
        time.sleep(1)

        """ 万向轮0mm """
        self.cmd = 'wheellift -su 0'
        self.send_command()
        time.sleep(1)

        """ 刮条下降 """
        self.cmd = 'scraperlift -p 2'
        self.send_command()
        time.sleep(2)

        self.cmd = 'io -h'
        self.send_command()
        time.sleep(0.2)
        self.temp_list.clear()  # 标志位开启之前清除temp_list
        self.receive_flag = 1
        time.sleep(3)
        self.receive_flag = 0

        # 参数提取
        print(self.temp_list)
        for i in range(0, len(self.temp_list)):
            for j in range(0, len(self.temp_list[i])):
                if self.temp_list[i][j:j + 10] == 'mopUp-left':
                    self.mopUp_left_0_list.append(int(self.temp_list[i][j + 11:j + 13].strip()))
                    self.mopUp_right_0_list.append(int(self.temp_list[i][j + 19:j + 21].strip()))
                elif self.temp_list[i][j:j + 11] == 'mopside-out':
                    self.mopside_in_0_list.append(int(self.temp_list[i][j + 17:j + 19].strip()))
                elif self.temp_list[i][j:j + 9] == 'roll_lift':
                    self.roll_lift_0_list.append(int(self.temp_list[i][j + 10:j + 12].strip()))
                elif self.temp_list[i][j:j + 13] == 'sideAdduction':
                    self.sideAdduction_0_list.append(int(self.temp_list[i][j + 14:j + 16].strip()))
                elif self.temp_list[i][j:j + 9] == 'wheellift':
                    self.wheellift_up_0_list.append(int(self.temp_list[i][j + 15:j + 17].strip()))
                elif self.temp_list[i][j:j + 13] == 'scraper front':
                    self.scraper_front_0_list.append(int(self.temp_list[i][j + 14:j + 16].strip()))

        print(f'mopUp_left_0_list为：{self.mopUp_left_0_list}')
        print(f'mopUp_right_0_list为：{self.mopUp_right_0_list}')
        print(f'mopside_in_0_list为：{self.mopside_in_0_list}')
        print(f'roll_lift_0_list为：{self.roll_lift_0_list}')
        print(f'sideAdduction_0_list为：{self.sideAdduction_0_list}')
        print(f'wheellift_up_0_list为：{self.wheellift_up_0_list}')
        print(f'scraper_front_0_list为：{self.scraper_front_0_list}')

        self.temp_list.clear()
        self.cmd= 'sideout -8000'
        time.sleep(6)
        self.send_command()
        time.sleep(2)
        self.cmd = 'scraperlift -p 0'
        self.send_command()
        time.sleep(2)
        self.cmd = '\\'
        self.send_command()
        time.sleep(3)

        #定义所有变量名list
        self.total_name_list = [self.batVolt_list,          self.batCurrent_list,       self.imuAccZ_list,                                          \
                                self.imuAccX_list,          self.imuAccY_list,          self.imuGryoX_list,                                         \
                                self.imuGryoY_list,         self.imuGryoZ_list,         self.yaw_list,              self.roll_list,                 \
                                self.pitch_list,            self.rollI_on_list,         self.rollI_off_list,        self.SOCEkfSend_list,           \
                                self.leftVel_f_list,        self.rightVel_f_list,       self.leftVel_r_list,        self.rightVel_r_list,           \
                                self.leftVel_stop_list,     self.rightVel_stop_list,    self.leftI_f_list,          self.rightI_f_list,             \
                                self.leftI_off_list,        self.rightI_off_list,       self.mopLI_on_list,         self.mopRI_on_list,             \
                                self.mopLI_off_list,        self.mopRI_off_list,        self.mopSideI_ext_list,     self.mopSideI_int_list,     \
                                self.mopSideI_ext_off_list, self.rollLiftI_on_list,     self.rollLiftI_off_list,    self.rollAngle_down_list,       \
                                self.rollAngle_up_list,     self.sideOutI_ext_list,     self.sideOutI_int_list,     self.sideOutI_ext_off_list,     \
                                self.fanRpm_on_list,        self.fanRpm_off_list,       self.fanCurrent_on_list,    self.fanCurrent_off_list,       \
                                self.CrossLI_1_list,        self.CrossLI_0_list,        self.CrossRI_1_list,        self.CrossRI_0_list,     \
                                self.CrossLVoltCtrl_1_list, self.CrossLVoltCtrl_0_list, self.CrossRVoltCtrl_1_list, self.CrossRVoltCtrl_0_list,     \
                                self.sideI_on_list,         self.sideI_off_list,        self.liftChassisUniversalI_on_list,self.liftChassisUniversalI_off_list,\
                                self.scraperLiftI_on_list,  self.scraperLiftI_off_list, self.echo1_list,            self.echo2_list,self.echo3_list,\
                                self.mopUp_left_0_list,     self.mopUp_left_1_list,     self.mopUp_right_0_list,    self.mopUp_right_1_list,        \
                                self.mopside_in_0_list,     self.mopside_in_1_list,     self.roll_lift_1_list,      self.roll_lift_0_list,          \
                                self.sideAdduction_0_list,  self.sideAdduction_1_list,  self.wheellift_up_0_list,   self.wheellift_up_1_list,       \
                                self.scraper_front_1_list,  self.scraper_front_0_list]

        df = pd.read_excel('点检参数配置.csv', 0, header=0)
        df = df.fillna(value=None,method='ffill',axis=None,inplace=False,limit=None)
        # df = df.fillna(value=None, method='ffill', axis=None, inplace=False, limit=None, downcast=None)
        self.var_name_list = df['var_name'].values.tolist()
        self.meaning_list  = df['meaning'].values.tolist()
        self.ref_min_list  = df['ref_min'].values.tolist()
        self.ref_max_list  = df['ref_max'].values.tolist()

        # 创建测量最大最小值的list,结果list
        self.result_list = []
        self.measured_min_list = []
        self.measured_max_list = []
        #
        for i in range(0,len(self.var_name_list)):
            self.result_list.append('')
            self.measured_min_list.append('')
            self.measured_max_list.append('')
        #结果判定
        for i in range(0,len(self.var_name_list)):
            if self.total_name_list[i] ==[]:
                self.measured_min_list[i] = '无数据'
                self.measured_max_list[i] = '无数据'
                self.result_list[i] = 'FAIL'
            #滚刷电机电流打开
            elif self.meaning_list[i] == '滚刷电机电流-打开' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i]:
                        self.cnt = self.cnt + 1
                if self.cnt >= 7 and self.measured_max_list[i] <=self.ref_max_list[i] :
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #左右抹布电流开启
            elif self.meaning_list[i] == '左抹布电流-开启' or self.meaning_list[i] =='右抹布电流-开启' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i]:
                        self.cnt = self.cnt + 1
                if self.cnt >= 7 and self.measured_max_list[i] <= self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #左右抹布电流关闭
            elif self.meaning_list[i] == '左抹布电流-关闭' or self.meaning_list[i] =='右抹布电流-关闭' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i] and self.total_name_list[i][j] <= self.ref_max_list[i]:
                        self.cnt = self.cnt + 1
                if self.cnt >= 10 :
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #抹布外扩-内收电流 边刷外扩-内收电流
            elif self.meaning_list[i] == '抹布外扩电流' or self.meaning_list[i] =='抹布内收电流' or self.meaning_list[i] =='边刷外扩电流' or self.meaning_list[i] =='边刷内收电流' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0,len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >=self.ref_min_list[i]:
                        self.cnt = self.cnt+1
                if self.cnt >=7 and self.measured_max_list[i] <=self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #左右越障电机电流到1
            elif self.meaning_list[i] == '左越障电机电流-到1' or self.meaning_list[i] =='右越障电机电流-到1':
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0,len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >=self.ref_min_list[i]:
                        self.cnt = self.cnt+1
                if self.cnt >=7 and self.measured_max_list[i] <=self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #左右越障电机电流到0
            elif self.meaning_list[i] == '左越障电机电流-到0' or self.meaning_list[i] =='右越障电机电流-到0':
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0,len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >=self.ref_min_list[i]:
                        self.cnt = self.cnt+1
                if self.cnt >=7 and self.measured_max_list[i] <=self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #左右越障电机电压到1
            elif self.meaning_list[i] == '左越障电机电压-到1' or self.meaning_list[i] =='右越障电机电压-到1':
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0,len(self.total_name_list[i])):
                    if self.total_name_list[i][j] ==self.ref_min_list[i]:
                        self.cnt = self.cnt+1
                if self.cnt >=7 and self.measured_max_list[i] <=self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #左右越障电机电压到0
            elif self.meaning_list[i] == '左越障电机电压-到0' or self.meaning_list[i] =='右越障电机电压-到0':
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0,len(self.total_name_list[i])):
                    if self.total_name_list[i][j] ==self.ref_min_list[i]:
                        self.cnt = self.cnt+1
                if self.cnt >=7 :
                    self.result_list[i] = 'PASS'
                    print(self.cnt)
                else:
                    self.result_list[i] = 'FAIL'

            #边刷电机电流-开启
            elif self.meaning_list[i] == '边刷电机电流-开启' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i]:
                        self.cnt = self.cnt + 1
                if self.cnt >= 7 and self.measured_max_list[i] <= self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #万向轮电流开启11mm
            elif self.meaning_list[i] == '万向轮电流-开启11mm' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                self.wheellift_cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i]:
                        self.cnt = self.cnt + 1
                    if self.total_name_list[i][j] >= 500:
                        self.wheellift_cnt = self.wheellift_cnt +1
                if self.cnt >= 7 and self.wheellift_cnt <=2 and self.measured_max_list[i] <= self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #万向轮电流关闭0mm
            elif self.meaning_list[i] == '万向轮电流-关闭0mm' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i]:
                        self.cnt = self.cnt + 1
                if self.cnt >= 7 and self.measured_max_list[i] <= self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            #挂条电机电流开启-关闭
            elif self.meaning_list[i] == '刮条电机电流-开启' or '刮条电机电流-关闭' :
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                self.cnt = 0
                for j in range(0, len(self.total_name_list[i])):
                    if self.total_name_list[i][j] >= self.ref_min_list[i]:
                        self.cnt = self.cnt + 1
                if self.cnt >= 7 and self.measured_max_list[i] <= self.ref_max_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
            else:
                self.measured_min_list[i] = min(self.total_name_list[i])
                self.measured_max_list[i] = max(self.total_name_list[i])
                if self.measured_max_list[i] <=self.ref_max_list[i] and self.measured_min_list[i] >=self.ref_min_list[i]:
                    self.result_list[i] = 'PASS'
                else:
                    self.result_list[i] = 'FAIL'
        #获取当前时间
        self.present_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        #使用xlsxwriter模块新建一个excel文件
        workbook = xlsxwriter.Workbook(f'{self.present_time}_点检处理结果.xlsx')
        worksheet = workbook.add_worksheet('Data')

        header_format = workbook.add_format({
            'bold': True,  # 加粗
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中（可选）
            'border': 1,  # 边框（1=细线）
        })

        contain_format = workbook.add_format({
            # 'bold': True,  # 加粗
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中（可选）
            # 'border': 1,  # 边框（1=细线）
        })
        # 写入列标题和数据
        worksheet.write(0, 0, "var_name", header_format)  # .write(行号,列号,内容)
        worksheet.write(0, 1, "meaning", header_format)
        worksheet.write(0, 2, "ref_min", header_format)
        worksheet.write(0, 3, "ref_max", header_format)
        worksheet.write(0, 4, "measured_min", header_format)
        worksheet.write(0, 5, "measured_max", header_format)
        worksheet.write(0, 6, "result", header_format)

        # 写入数据
        for row in range(len(self.var_name_list)):
            worksheet.write(row + 1, 0, self.var_name_list[row],contain_format)
            worksheet.write(row + 1, 1, self.meaning_list[row],contain_format)
            worksheet.write(row + 1, 2, self.ref_min_list[row],contain_format)
            worksheet.write(row + 1, 3, self.ref_max_list[row],contain_format)
            worksheet.write(row + 1, 4, self.measured_min_list[row],contain_format)
            worksheet.write(row + 1, 5, self.measured_max_list[row],contain_format)
            worksheet.write(row + 1, 6, self.result_list[row],contain_format)

        #构造处理结果文件
        # data = {'var_name':self.var_name_list,'meaning':self.meaning_list,'ref_min':self.ref_min_list,'ref_max':self.ref_max_list,\
        #         'measured_min':self.measured_min_list,'measured_max':self.measured_max_list,'result':self.result_list}
        # df_result= pd.DataFrame(data)
        # df_result.to_excel(f'{self.present_time}_点检处理结果.xlsx', index=False)
        #构造dict
        dic = {}
        for i in range(0,len(self.total_name_list)):
            dic[self.meaning_list[i]] = self.total_name_list[i]
        #将dict写入txt
        with open(f'{self.present_time}_提取Xshell打印数据.txt', 'w', encoding='utf-8') as f:
            for key, value in dic.items():
                f.write(f"{key:<20}: {value}\n")

        red_format = workbook.add_format({'bg_color': '#FF0000'})
        green_format = workbook.add_format({'bg_color': '#00FF00'})
        # 假设要检查的列是 A 列（范围 A1:A10），值为 "FAIL" 时变红
        worksheet.conditional_format('G2:G74', {
            'type': 'text',  # 文本匹配类型
            'criteria': 'containing',  # 包含特定文本（也可用 'equal to' 精确匹配）
            'value': 'FAIL',  # 目标值
            'format': red_format  # 应用的格式
        })
        worksheet.conditional_format('G2:G74', {
            'type': 'text',  # 文本匹配类型
            'criteria': 'containing',  # 包含特定文本（也可用 'equal to' 精确匹配）
            'value': 'PASS',  # 目标值
            'format': green_format  # 应用的格式
        })

        #设置列宽
        worksheet.set_column('A:A', 28)
        worksheet.set_column('B:B', 22)
        #冻结第一行
        worksheet.freeze_panes(1, 0)
        #  保存文件
        workbook.close()
        self.flag_inside_cmd = 0
        print('开启外部输入命令')
        # self.append_receive(f"一键处理完成，可选择退出软件或者执行其他操作")
        return

    #因为echo打印的参数和其他打印参数的格式不同，所以需要重新设计一个提取超声波参数的函数
    def echo_extr(self,temp_list=[],var_name=''):
        l = len(var_name)
        result_list = []
        for i in range(0,len(temp_list)):
            for j in range(0,len(temp_list[i])):
                if temp_list[i][j:j+l] == var_name :
                    result_list.append(int(temp_list[i][j+6:j+11].strip()))
        return result_list

    def io_h_extr(self,temp_list=[],var_name=''):
        l = len(var_name)
        result_list = []
        for i in range(0,len(temp_list)):
            for j in range(0,len(temp_list[i])):
                if temp_list[i][j:j+l] == var_name :
                    result_list.append(int(temp_list[i][j+6:j+11].strip()))
        return  result_list

    def send_command(self):
        """发送指令"""
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接串口")
            return
        if self.flag_inside_cmd ==0:
            self.cmd = self.cmd_entry.get().strip()
        if not self.cmd:
            return
        try:
            # 添加换行符如果指令中没有
            if not self.cmd.endswith('\n'): #endswith是str类中的一个方法，判断字符串以什么字符结尾
                self.cmd += '\n'
            self.ser.write(self.cmd.encode()) #串口发送self.cmd.encode(),encode（）是str类中的方法，将字符串转换为字节
            self.append_receive(f"send: {self.cmd.strip()}\n")
            self.cmd_entry.delete(0, tk.END)
            print('发送命令结束')
            # time.sleep(3)
        except Exception as e:
            messagebox.showerror("发送错误", f"发送指令失败: {str(e)}")

    def append_receive(self, text):
        """在接收区域添加文本"""
        self.recv_text.insert(tk.END, text)
        self.recv_text.see(tk.END)

    def receive_data(self):
        # self.temmp_list = []
        data=''
        print('接收数据线程')
        """接收数据线程"""
        # while 1:
        while self.is_connected and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode().strip() #ser.readline()读取一行数据
                    # with open('temp_list.txt', 'a') as f:
                    #     f.write(f'{data}\n')
                    # if self.cmd == 'info -a\n':
                        # with open('para_list.txt', 'a') as f:
                        #     f.write(f'{data}\n')
                        # print(self.data)
                        # if data[0] == '*':
                        # if data != '' and data !='>>':
                        #     self.para_list.append(f'{data}')
                        # print(self.para_list)
                        # self.batVolt_list.append(f'{self.data}')
                    # elif  self.first_flag ==1:
                    #     if data != '' and data !='>>' and data != '/':
                    #         self.temp_list.append(f"{data}")
                    #         # print(self.first_list)
                    # elif  self.rollI_on_cmd_flag ==1 :
                    #     if data != '' and data !='>>' and data != '/':
                    #         self.temp_list.append(f'{data}')
                    if  self.receive_flag ==1 :
                        if data != '' and data !='>>' and data != '/':
                            self.temp_list.append(f'{data}')
                    if data:
                        self.received_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        # print(self.received_time)
                        self.append_receive(f"received:{self.received_time} {data}\n")   #调用显示方法
                time.sleep(0.01)

            except Exception as e:
                if self.is_connected:  # 只有在连接状态下才显示错误
                    self.append_receive(f"接收错误: {str(e)}\n")
                break
    def clear_receive(self):
        """清空接收区域"""
        self.recv_text.delete(1.0, tk.END)
    
    def save_data(self):
        """保存接收到的数据到文件"""
        try:
            self.present_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            data = self.recv_text.get(1.0, tk.END)
            if data.strip():
                with open(f"{self.present_time}_Xshell打印原始数据.txt", "w", encoding="utf-8") as f:
                    f.write(data)
                messagebox.showinfo(f"保存成功", "数据已保存到 {self.present_time}_Xshell打印原始数据.txt")
            else:
                messagebox.showwarning("无数据", "接收区域没有数据可保存")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存数据失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()      #Tk是class，root为对象
    app = SerialTool(root)
    root.mainloop()