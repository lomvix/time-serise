import pymysql
import numpy as np
import time,datetime
import vmd
import tensorflow as tf
import matplotlib.pyplot as plt
import requests
import keras
from keras.layers.core import Dense, Dropout
from keras.layers.recurrent import LSTM,GRU
from keras.layers import Input
from keras.models import Model
from keras import backend as K
from keras.models import load_model
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import copy
import sys

# 打印运行信息
class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
	    self.terminal = stream
	    self.log = open(filename, 'a')

    def write(self, message):
	    self.terminal.write(message)
	    self.log.write(message)

    def flush(self):
	    pass

# 返回时间戳
def timetostamp(current_time):
    now_times = current_time.strftime("%Y-%m-%d %H:%M:%S")
    now_timeArray = time.strptime(now_times, "%Y-%m-%d %H:%M:%S")
    now_timeStamp = int(time.mktime(now_timeArray))
    return now_timeStamp

# 时间戳转换为日期
def timestamptodate(timestamp):
    timeArray = time.localtime(timestamp)
    str_datetime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return str_datetime

#字符串转为时间戳
def strtotimestamp(stringtime):
    date1 = time.strptime(stringtime, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(date1))
    return timestamp

# 返回机组开机后运行时间
def already_runtime(timelist,start_runtime,interval_time):
    runtime_list = []
    timestamp_list =[]
    for i in range(len(timelist)):
        temptimestamp = strtotimestamp(timelist[i])
        timestamp_list.append(temptimestamp)
    for i in range(len(timelist)):
        if i == 0:
            runtime_list.append(start_runtime)
            continue
        if timestamp_list[i] - timestamp_list[i-1] == interval_time:
            temp_runtime = runtime_list[i-1] + interval_time
            runtime_list.append(temp_runtime)
        elif timestamp_list[i] - timestamp_list[i-1] != interval_time:
            temp_runtime = start_runtime
            runtime_list.append(temp_runtime)
    return runtime_list

# 时段查询，返回时间段
def timeframe_query_old(id,starttime,endtime,sub_thrshold,up_threshold,datalag,datatype,url):#使用时将函数名改为timeframe_query
    id = str(id)
    datatype = str(datatype)
    datalag = str(datalag)
    sub_thrshold = str(sub_thrshold)
    up_threshold = str(up_threshold)
    starttime = str(starttime) + '000'
    endtime = str(endtime) + '000'
    if datatype == '0':
        url_params = {'id': id, 'starttime': starttime, 'endtime': endtime, 'sub-thrshold': sub_thrshold,
                  'up-threshold': up_threshold, 'datatype': datatype, 'datalag': datalag}
    elif datatype =='1':
        url_params = {'id': id, 'starttime': starttime, 'endtime': endtime,'datatype': datatype, 'datalag': datalag}
    try:
        r= requests.get(url,params=url_params)
        results = r.json()['result']
    except:
        print('uable to fetch data!')
        results = []
    resultdata = []
    if results == None or len(results)==0:
        return resultdata
    for i in range(len(results)):
        resultdata.append([])
    for i in range(len(results)):
        resultdata[i].append(int(results[i]['starttime']))
        resultdata[i].append(int(results[i]['endtime']))
    return resultdata

def timeframe_query(id,starttime,endtime,sub_thrshold,up_threshold,datalag,datatype,url):
    id = str(id)
    datatype = str(datatype)
    datalag = str(datalag)
    sub_thrshold = str(sub_thrshold)
    up_threshold = str(up_threshold)
    starttime = str(starttime) + '000'
    endtime = str(endtime) + '000'
    if datatype == '0':
        url_params = {'id': id, 'starttime': starttime, 'endtime': endtime, 'sub-thrshold': sub_thrshold,
                  'up-threshold': up_threshold, 'datatype': datatype, 'datalag': datalag}
        url = "http://47.97.9.120:8080/device/tempfloat/timefloatlist"
    elif datatype =='1':
        url_params = {'id': id, 'starttime': starttime, 'endtime': endtime,'datatype': datatype, 'datalag': datalag}
        url = "http://47.97.9.120:8080/device/tempbool/timeboollist"
    try:
        r= requests.get(url,params=url_params)
        results = r.json()['result']
    except:
        print('uable to fetch data!')
        results = []
    resultdata = []
    if results == None or len(results)==0:
        return resultdata
    for i in range(len(results)):
        resultdata.append([])
    for i in range(len(results)):
        resultdata[i].append(int(results[i]['starttime']))
        resultdata[i].append(int(results[i]['endtime']))
    return resultdata


# 基本查询，返回指定时段值，结果为时间和值
def basic_query_old(id,datatype,starttime,endtime,interval,url):#使用时将函数名改为basic_query
    # readstart = time.clock()
    id = str(id)
    datatape=str(datatype)
    starttime = str(starttime) + '000'
    endtime = str(endtime) + '000'
    interval = str(interval)
    url_params = {'id': id, 'datatype': datatype, 'starttime': starttime, 'endtime': endtime,
                  'interval': interval}
    try:
        r = requests.get(url, params=url_params)
        results = r.json()['result']
    except:
        print('uable to fetch data!')
        results = []
    # readend = time.clock()
    resultdata = []
    if results == None or len(results)==0:
        return resultdata
    for i in range(len(results)):
        resultdata.append([])
    for i in range(len(results)):
        resultdata[i].append(results[i]['tm'])
        resultdata[i].append(results[i]['value'])
    # print('getdatatime：',readend-readstart)
    return resultdata

#仙居项目重构
def basic_query(id,datatype,starttime,endtime,interval,url):
    # readstart = time.clock()
    id = str(id)
    datatype=str(datatype)
    starttime = str(starttime) + '000'
    endtime = str(endtime) + '000'
    interval = str(interval)
    url_params = {'id': id, 'datatype': datatype, 'starttime': starttime, 'endtime': endtime,
                  'interval': interval}

    if datatype == '0':
        url = "http://111.172.229.145:50001/device/tempfloat/tempfloatlist"
    elif datatype == '1':
        url = "http://111.172.229.145:50001/device/tempbool/tempboollist"
    try:
        r = requests.get(url, params=url_params)
        results = r.json()['result']
    except:
        print('uable to fetch data!')
        results = []
    # readend = time.clock()
    resultdata = []
    if results == None or len(results)==0:
        return resultdata
    for i in range(len(results)):
        resultdata.append([])
    for i in range(len(results)):
        resultdata[i].append(results[i]['time'])
        resultdata[i].append(results[i]['value'])
    # print('getdatatime：',readend-readstart)
    return resultdata


# 处理查询的bool结果去除重复点
def deal_boolresult(bool_result):
    if len(bool_result) == 0:
        return []
    bool_result1 = []
    stateflag = 0
    for i in range(len(bool_result)):
        if i ==0 and bool_result[i][1] == 0:
            bool_result1.append(bool_result[i])
        elif bool_result[i][1] == 1 and stateflag == 0:
            stateflag = 1
            bool_result1.append(bool_result[i])
        elif bool_result[i][1] == 0 and stateflag == 1:
            stateflag = 0
            bool_result1.append(bool_result[i])
    return bool_result1

# 查询指定时间内完整的抽水或发电时间
def get_completetime(unitstate,starttimestamp,endtimestamp,url1):
    timelist = []
    result_timelist = []
    starttimestamp1 = starttimestamp-24*60*60
    timelist1 = basic_query(unitstate,1,starttimestamp,endtimestamp,-1,url1)
    timelist2 = basic_query(unitstate, 1, starttimestamp1, starttimestamp, -1, url1)
    timelist1 = deal_boolresult(timelist1)
    timelist2 = deal_boolresult(timelist2)
    if len(timelist1) == 0:
        return []
    if len(timelist2) >0 and timelist2[-1][1] == 1 :
        timelist.append(timelist2[-1][0])
        flag = -1
        for i in range(len(timelist1)):
            if  timelist1[i][1] == 0:
                flag = i
                timelist.append(timelist1[i][0])
                break
        if len(timelist1)-1 > flag and flag > -1:
            for j in range(flag+1,len(timelist1)):
                if j == len(timelist1) and timelist1[j][1] == 1:
                    continue
                timelist.append(timelist1[j][0])
    elif (len(timelist2) ==0) or (len(timelist2) >0 and timelist2[-1][1] == 0 ):
        for i in range(len(timelist1)):
            if (i == 0 and timelist1[i][1] == 0):
                continue
            elif (i == len(timelist1)-1 and timelist1[i][1] == 1):
                continue
            else:
                timelist.append(timelist1[i][0])
    if len(timelist) == 0 :
        return []
    dim = int(len(timelist)/2)
    for i in range(dim):
        result_timelist.append([])
        result_timelist[i].append(timelist[2*i])
        result_timelist[i].append(timelist[2*i+1])
    return result_timelist

# 获取前一天的数据，延迟一段开始时间并提前一段结束时间，间隔取数据
def getrealdata_url(starttimestamp,endtimestamp,unit_state,data_idlist,sampleInterval,delaytime,advancetime,url1):
    timeframe_list = get_completetime(unit_state,starttimestamp,endtimestamp,url1)
    datalist = []
    for i in range(len(data_idlist)):
        datalist.append([])
    for i in range(len(data_idlist)):
        tempdata = []
        for j in range(len(timeframe_list)):
            float_result = basic_query(data_idlist[i],0,timeframe_list[j][0],timeframe_list[j][1],0,url1)
            if len(float_result)==0:
                continue
            starttime = float_result[0][0] + delaytime
            endtime = float_result[-1][0] - advancetime
            if (endtime-starttime) <= sampleInterval:
                continue
            if (endtime-starttime) > sampleInterval:
                datanum = (endtime-starttime)/sampleInterval
                datanum = int(datanum + 1)
            startindex = get_index(float_result,starttime)
            for k in range(datanum):
                temp_time = float_result[startindex + k*sampleInterval][0]
                temp_value = float_result[startindex + k*sampleInterval][1]
                local_time = time.localtime(temp_time)
                local_timesd = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                datalist[i].append([local_timesd, temp_value])
    return datalist


# 获取数据，延迟一段开始时间并提前一段结束时间，间隔取数据
def getdata_url(starttimestamp,endtimestamp,unit_state,data_idlist,sampleInterval,delaytime,advancetime,url1,url2):
    timeframe_list = timeframe_query(unit_state,starttimestamp,endtimestamp,0,1,1,1,url2)
    datalist = []
    for i in range(len(data_idlist)):
        datalist.append([])
    for i in range(len(data_idlist)):
        tempdata = []
        for j in range(len(timeframe_list)):
            float_result = basic_query(data_idlist[i],0,timeframe_list[j][0],timeframe_list[j][1],0,url1)
            if len(float_result)==0:
                continue
            starttime = float_result[0][0] + delaytime
            endtime = float_result[-1][0] - advancetime
            if (endtime-starttime) <= sampleInterval:
                continue
            if (endtime-starttime) > sampleInterval:
                datanum = (endtime-starttime)/sampleInterval
                datanum = int(datanum + 1)
            startindex = get_index(float_result,starttime)
            for k in range(datanum):
                temp_time = float_result[startindex + k*sampleInterval][0]
                temp_value = float_result[startindex + k*sampleInterval][1]
                local_time = time.localtime(temp_time)
                local_timesd = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                datalist[i].append([local_timesd, temp_value])
    return datalist

#   获取历史抽水、发电下稳态健康模型数据
def get_steady_health_hisdata1(maintenance_time, timelength,url,pumpstate_id,powerstate_id, data_idlist,sampleInterval):
    data_pump, data_power, result_pump, result_power = [], [], [], []
    starttime = maintenance_time
    endtime = maintenance_time + timelength
    for index in range(len(data_idlist)):
        data_pump.append([])
        data_power.append([])
    pump_bool_result = basic_query(pumpstate_id, 1, starttime, endtime, interval=-1, url=url)
    power_bool_result = basic_query(powerstate_id, 1, starttime, endtime, interval=-1, url=url)
    for i in range(len(data_idlist)):
        tempdata_pump, tempdata_power, temp_pump, temp_power = [], [], [],[]
        pump_time = 0
        power_time = 0
        float_result = basic_query(data_idlist[i],0,starttime,endtime,interval=-1,url=url)
        [tempdata_pump,temp_pumptime] = steady_health_datalist(float_result,pump_bool_result,sampleInterval)
        [tempdata_power,temp_powertime] = steady_health_datalist(float_result,power_bool_result,sampleInterval)
        data_pump[i] = data_pump[i] + tempdata_pump
        data_power[i] = data_power[i] + tempdata_power
        pump_time = pump_time +temp_pumptime
        power_time = power_time + temp_powertime
        temp_pump = get_listrow(1,data_pump[i])
        temp_power = get_listrow(1,data_power[i])
        result_pump.append(temp_pump)
        result_power.append(temp_power)
    return result_pump, result_power

# 获取历史抽水、发电下稳态劣化模型数据
def get_steady_deter_hisdata1(starttime, timelength,url,pumpstate_id,powerstate_id, data_idlist):
    data_pump = []
    data_power = []
    result_pump = []
    result_power = []
    result_pumptime = []
    result_powertime=[]
    endtime = starttime + timelength
    for index in range(len(data_idlist)):
        data_pump.append([])
        data_power.append([])
    pump_bool_result = basic_query(pumpstate_id, 1, starttime, endtime, interval=-1, url=url)
    power_bool_result = basic_query(powerstate_id, 1, starttime, endtime, interval=-1, url=url)
    for i in range(len(data_idlist)):
        tempdata_pump = [];tempdata_power = []; temp_pump = []; temp_power = [];temp_pumptime =[];temp_powertime =[]
        float_result = basic_query(data_idlist[i],0,starttime,endtime,interval=-1,url=url)
        tempdata_pump = steady_deter_datalist(float_result,pump_bool_result)
        tempdata_power = steady_deter_datalist(float_result,power_bool_result)
        data_pump[i] = data_pump[i] + tempdata_pump
        data_power[i] = data_power[i] + tempdata_power
        temp_pump = get_listrow(1,data_pump[i])
        temp_power = get_listrow(1,data_power[i])
        result_pumptime = get_listrow(0,data_pump[i])
        result_powertime = get_listrow(0,data_power[i])
        result_pump.append(temp_pump)
        result_power.append(temp_power)
    return result_pump, result_power,result_pumptime,result_powertime

def read_bool_data(host, user, password, port,table_id,table_year,table_month):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    if table_month < 10:
        table_month = str(0) + str(table_month)
    else:
        table_month = str(table_month)
    table_name = 'bool'+ '_' + str(table_id) + '_'+ str(table_year) + '_' + table_month
    sql = "SELECT * FROM " + str(table_name)
    results=[]
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print('fetch data!')
    except:
        print('Uable to fetch data!')
    conn.close()
    return results

def read_float_data(host, user, password, port,table_id,table_year,table_month):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    if table_month < 10:
        table_month = str(0) + str(table_month)
    else:
        table_month = str(table_month)
    table_name = 'float'+ '_' + str(table_id) + '_'+ str(table_year) + '_' + table_month
    sql = "SELECT * FROM " + str(table_name)
    results = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print('fetch data!')
    except:
        print('Uable to fetch data!')
    conn.close()
    return results

def steady_health_datalist(float_result,bool_result,sample_interval):
    stateflag = 0
    timelist1 = [];timelist2 =[]
    steady_list =[]
    for i in range(len(bool_result)):
        if i == len(bool_result)-1 and stateflag == 0 and bool_result[i][1] == 1:
            continue
        elif i == len(bool_result)-1 and stateflag == 1 and bool_result[i][1] ==1:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] ==1 and stateflag ==0:
            stateflag = 1;
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] ==0 and stateflag == 1:
            stateflag = 0
            timelist1.append(bool_result[i][0])
#     取开机后一小时到关机前10分钟的稳态数据的平均值
    tdim = int(len(timelist1) / 2)
    for i in range(tdim):
        temptime = timelist1[2 * i]
        temptime = temptime + 60 *60
        if temptime > timelist1[2 * i + 1] - 600:
            continue
        else:
            timelist2.append(temptime)
            temptime = timelist1[2 * i + 1] - 600
            timelist2.append(temptime)
    if len(timelist2) ==0:
        return steady_list,tdim
    aver_time, aver_index = average_time(timelist2,float_result,sampleInterval=sample_interval)
    if aver_time == []:
        return steady_list,tdim
    for i in range(len(aver_time)):
        for j in range(len(aver_time[i])-1):
            start_index = aver_index[i][j]
            end_index = aver_index[i][j+1]
            sum_value = 0; aver_value = 0; k=0
            if start_index == end_index:
                aver_value = float_result[start_index][1]
            else:
                for k in range(start_index,end_index):
                    sum_value = sum_value + float_result[k][1]
                aver_value = sum_value/(end_index - start_index)
            start_time = aver_time[i][j]
            local_time = time.localtime(start_time)
            local_timesd = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            steady_list.append([local_timesd,aver_value])
    return steady_list,tdim

def average_time(timelist,float_result,sampleInterval):
    dim = len(timelist)/2
    dim = int(dim)
    aver_time =[]
    aver_index = []
    if dim == 0 or len(float_result) == 0:
        return aver_time,aver_index
    for i in range(dim):
        aver_time.append([])
        aver_index.append([])
        if (timelist[2*i + 1]-timelist[2*i]) < sampleInterval:
            aver_time[i].append(timelist[2*i])
            aver_time[i].append(timelist[2*i + 1])
            for m in range(2):
                tempt = aver_time[i][m]
                temp_index = get_index(float_result,tempt)
                aver_index[i].append(temp_index)
        else:
            tempt = (timelist[2*i+1]-timelist[2*i])/sampleInterval
            tempt = int(tempt+1)
            for j in range(tempt):
                temp_time = timelist[2*i] + sampleInterval*j
                aver_time[i].append(temp_time)
                temp_index = get_index(float_result,temp_time)
                aver_index[i].append(temp_index)
    return aver_time,aver_index

def get_index(float_result,temp_time):
    n = len(float_result)
    if temp_time == float_result[n-1][0]:
        return n-1
    elif temp_time < float_result[0][0]:
        return 0
    elif temp_time > float_result[n-1][0]:
        return n-1
    for i in range(n-1):
        if temp_time == float_result[i][0]:
            return i
        elif temp_time >float_result[i][0] and temp_time<float_result[i+1][0]:
            return i


# 计算时域指标
def time_feature(datalist):
    datalist = np.array(datalist)
    N = len(datalist)
    # p1 = sum(abs(datalist))/N
    p1 = sum(datalist) / N
    p2 = np.sqrt(sum((datalist - p1) ** 2) / (N - 1))
    p3 = (sum(np.sqrt(abs(datalist))) / N) ** 2
    p4 = np.sqrt(sum(datalist ** 2) / N)
    p5 = max(abs(datalist))
    p6 = sum((datalist - p1) ** 3) / ((N - 1) * (p2 ** 3))
    p7 = sum((datalist - p1) ** 4) / ((N - 1) * (p2 ** 4))
    p8 = p5 / p4
    p9 = p5 / p3
    p10 = p4 / (sum(abs(datalist)) / N)
    p11 = p5 / (sum(abs(datalist)) / N)
    return [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]

# 获取插值模式下历史抽水、发电下数据
def get_hisdata(host, user, password, bool_port, float_port, pump_state,power_state, datalist,
                     year, month, sampleInterval,delaytime,advancetime):
    data_pump = []; data_power = []; result_pump = []; result_power = [];
    for index in range(len(datalist)):
        data_pump.append([])
        data_power.append([])
    for i in range(len(datalist)):
        tempdata_pump = [];tempdata_power = []; temp_pump = []; temp_power = []
        pump_time = 0;power_time = 0
        for j in range(len(year)):
            for k in range(len(month[j])):
                readstart1 = time.clock()
                y = year[j]; m = month[j][k]
                pump_bool_result = read_bool_data(host, user, password, bool_port,pump_state,y, m)
                power_bool_result = read_bool_data(host, user, password, bool_port,power_state,y, m)
                float_result = read_float_data(host, user, password, float_port, datalist[i] ,y,m)
                tempdata_pump = get_datalist(float_result,pump_bool_result,sampleInterval,delaytime,advancetime)
                tempdata_power = get_datalist(float_result,power_bool_result,sampleInterval,delaytime,advancetime)
                data_pump[i] = data_pump[i] + tempdata_pump
                data_power[i] = data_power[i] + tempdata_power
                readend1 = time.clock()
                print('取一个月的时间：',readend1-readstart1)
        result_pump.append(data_pump[i])
        result_power.append(data_power[i])
    return result_pump, result_power

# 获取插值模式下历史抽水、发电下数据
def get_originaldata(host, user, password, bool_port, float_port, pump_state, power_state, datalist,
                     year, month, sampleInterval, delaytime, advancetime):
    data_pump = []
    data_power = []
    result_pump = []
    result_power = []
    for index in range(len(datalist)):
        data_pump.append([])
        data_power.append([])
    for i in range(len(datalist)):
        tempdata_pump = []
        tempdata_power = []
        temp_pump = []
        temp_power = []
        pump_time = 0
        power_time = 0
        for j in range(len(year)):
            for k in range(len(month[j])):
                readstart1 = time.clock()
                y = year[j]
                m = month[j][k]
                pump_bool_result = read_bool_data(host, user, password, bool_port, pump_state, y, m)
                power_bool_result = read_bool_data(host, user, password, bool_port, power_state, y, m)
                float_result = read_float_data(host, user, password, float_port, datalist[i], y, m)
                tempdata_pump = get_originaldatalist(float_result, pump_bool_result, sampleInterval, delaytime,
                                                     advancetime)
                tempdata_power = get_originaldatalist(float_result, power_bool_result, sampleInterval, delaytime,
                                                      advancetime)
                data_pump[i] = data_pump[i] + tempdata_pump
                data_power[i] = data_power[i] + tempdata_power
                readend1 = time.clock()
                print('取一个月的时间：', readend1 - readstart1)
        result_pump.append(data_pump[i])
        result_power.append(data_power[i])
    return result_pump, result_power

 # 取抽水发电态下数据，插值模式每隔interval取一点，延迟取数据，提前结束取数据
def get_originaldatalist(float_result, bool_result, sample_interval, delaytime, advancetime):
    stateflag = 0
    timelist1 = []
    timelist2 = []
    datalist = []
    for i in range(len(bool_result)):
        if i == len(bool_result) - 1 and stateflag == 0 and bool_result[i][1] == 1:
            continue
        elif i == len(bool_result) - 1 and stateflag == 1 and bool_result[i][1] == 1:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] == 1 and stateflag == 0:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] == 0 and stateflag == 1:
            stateflag = 0
            timelist1.append(bool_result[i][0])
    if len(timelist1) == 0:
        return datalist
    tdim = int(len(timelist1) / 2)
    for i in range(tdim):
        temptime = timelist1[2 * i]
        temptime = temptime + delaytime
        if temptime > timelist1[2 * i + 1] - advancetime:
            continue
        else:
            timelist2.append(temptime)
            temptime = timelist1[2 * i + 1] - advancetime
            timelist2.append(temptime)
    if len(timelist2) == 0:
        return datalist
    for i in range(int(len(timelist2) / 2)):
        datalist.append([])
    aver_time, aver_index = aver_timeindex(timelist2, float_result, sampleInterval=sample_interval)
    if aver_time == []:
        return datalist
    for i in range(len(aver_time)):
        for j in range(len(aver_time[i])):
            start_index = aver_index[i][j]
            start_time = aver_time[i][j]
            tempvalue = float_result[start_index][1]
            local_time = time.localtime(start_time)
            local_timesd = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            datalist[i].append([local_timesd, tempvalue])
    return datalist

# 取抽水发电态下数据，插值模式每隔interv取一个平均,延迟取数据，提前结束取数据
def get_datalist(float_result,bool_result,sample_interval,delaytime,advancetime):
    stateflag = 0
    timelist1 = []
    timelist2 =[]
    datalist =[]
    for i in range(len(bool_result)):
        if i == len(bool_result)-1 and stateflag == 0 and bool_result[i][1] == 1:
            continue
        elif i == len(bool_result)-1 and stateflag == 1 and bool_result[i][1] ==1:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] ==1 and stateflag ==0:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] ==0 and stateflag == 1:
            stateflag = 0
            timelist1.append(bool_result[i][0])
    if len(timelist1) ==0:
        return datalist
    tdim = int(len(timelist1) / 2)
    for i in range(tdim):
        temptime = timelist1[2 * i]
        temptime = temptime + delaytime
        if temptime > timelist1[2 * i + 1] - advancetime:
            continue
        else:
            timelist2.append(temptime)
            temptime = timelist1[2 * i + 1] - advancetime
            timelist2.append(temptime)
    if len(timelist2) == 0:
        return datalist
    for i in range(int(len(timelist2)/2)):
        datalist.append([])
    aver_time, aver_index = aver_timeindex(timelist2, float_result, sampleInterval=sample_interval)
    if aver_time == []:
        return datalist
    for i in range(len(aver_time)):
        for j in range(len(aver_time[i])-1):
            start_index = aver_index[i][j]
            end_index = aver_index[i][j+1]
            sum_value = 0; aver_value = 0; k=0
            if start_index == end_index:
                aver_value = float_result[start_index][1]
            else:
                for k in range(start_index,end_index):
                    sum_value = sum_value + float_result[k][1]
                aver_value = sum_value/(end_index - start_index)
            start_time = aver_time[i][j]
            local_time = time.localtime(start_time)
            local_timesd = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            datalist[i].append([local_timesd,aver_value])
    return datalist

# 获取插值下的平均时间和索引
def aver_timeindex(timelist, float_result, sampleInterval):
    dim = len(timelist)/2
    dim = int(dim)
    aver_time =[]
    result_avertime =[]
    result_averindex =[]
    aver_index = []
    if dim == 0 or len(float_result) == 0:
        return aver_time,aver_index
    for i in range(dim):
        aver_time.append([])
        aver_index.append([])
        if (timelist[2*i + 1]-timelist[2*i]) < sampleInterval:
            continue
        if(timelist[2*i + 1]-timelist[2*i]) > sampleInterval:
            tempt = (timelist[2*i+1]-timelist[2*i])/sampleInterval
            tempt = int(tempt+1)
            start_index = get_index(float_result,timelist[2*i])
            for j in range(tempt):
                temp_time = timelist[2*i] + sampleInterval*j
                aver_time[i].append(temp_time)
                temp_index = start_index + sampleInterval*j
                aver_index[i].append(temp_index)
    for i in range(len(aver_time)):
        if len(aver_time[i]) ==0:
            continue
        result_avertime.append(aver_time[i])
        result_averindex.append(aver_index[i])
    return result_avertime,result_averindex

#去掉时间，将每个过程的数据放一起
def inidatatolist(ini_data):
    datalist = []
    for i in range(len(ini_data)):
        datalist.append([])
        for j in range(len(ini_data[i])):
            datalist[i].append([])
    for i in range(len(ini_data)):
        for j in range(len(ini_data[i])):
            for k in range(len(ini_data[i][j])):
                datalist[i][j].append(ini_data[i][j][k][1])
    return datalist

# 二维不规则数组最大最小值
def maxmin_list(arraylist):
    maxlist = []
    minlist =[]
    for i in range(len(arraylist)):
        max1 = max(arraylist[i])
        min1 = min(arraylist[i])
        maxlist.append(max1)
        minlist.append(min1)
    maxval = np.array(maxlist).max()
    minval = np.array(minlist).min()
    return maxval,minval

#二维不规则数组最大最小归一化
def minmax_scaling1(datalist, direction="apply", maxmin=None):
    if direction == "apply":
        result_list =[]
        maxval = maxmin[0]
        minval = maxmin[1]
        for i in range(len(datalist)):
            tempdata = (datalist[i] - minval) / (maxval - minval)
            result_list.append(tempdata)
        result_list = np.array(result_list)
        return result_list
    if direction == "reverse":
        maxval = maxmin[0]
        minval = maxmin[1]
        for i in range(len(datalist)):
            datalist[i] = datalist[i] * (maxval - minval) + minval
        return datalist

#最大最小归一化
def minmax_scaling(datalist, direction="normal", maxmin=None):
    if direction == "normal":
        datalist1 = np.array(datalist)
        datalist1 = abs(datalist1)
        maxval = datalist1.max()
        minval = datalist1.min()
        resultlist = (datalist1 - minval) / (maxval - minval)
        return resultlist, [maxval, minval]
    if direction == "apply":
        datalist1 = np.array(datalist)
        datalist1 = abs(datalist1)
        maxval = maxmin[0]
        minval = maxmin[1]
        resultlist = (datalist1 - minval) / (maxval - minval)
        return resultlist
    if direction == "reverse":
        datalist1 = np.array(datalist)
        maxval = maxmin[0]
        minval = maxmin[1]
        resultlist = datalist1 * (maxval - minval) + minval
        return resultlist

# 0均值标准化
def Zscore_standardization(datalist,direction = "normal",meanstd=None):
    datalist = np.array(datalist)
    if direction == "normal":
        meanval = datalist.mean()
        stdval = datalist.std()
        resultlist = (datalist-meanval)/stdval
        return resultlist, [meanval, stdval]
    if direction == "apply":
        meanval = meanstd[0]
        stdval = meanstd[1]
        resultlist = (datalist-meanval)/stdval
        return resultlist
    if direction == "reverse":
        meanval = meanstd[0]
        stdval = meanstd[1]
        resultlist = datalist*stdval + meanval
        return resultlist

# 检查每个id读的数据长度是否一致
def   check_hisdata(datalist, starttimestamp, endtimestamp, stateid, idlist, sampleInterval, delaytime, advancetime, url1, url2):
    lenlist = []
    for i in range(len(datalist)):
        templen = len(datalist[i])
        lenlist.append(templen)
    lenlist=np.array(lenlist)
    for i in range(len(datalist)):
        if lenlist[i] != max(lenlist):
            while True:
                tempdatalist = getdata_url(starttimestamp, endtimestamp, stateid, [idlist[i]],sampleInterval, delaytime, advancetime, url1, url2)
                if len(tempdatalist[0]) == max(lenlist):
                    datalist[i] = tempdatalist[0]
                    break
    return datalist

# 检查每个id读的数据长度是否一致,读十次，如果不行就不再读了
# def check_realdata(datalist, starttimestamp, endtimestamp, stateid, idlist, sampleInterval, delaytime, advancetime, url1):
#     lenlist = []
#     for i in range(len(datalist)):
#         templen = len(datalist[i])
#         lenlist.append(templen)
#     lenlist=np.array(lenlist)
#     for i in range(len(datalist)):
#         if lenlist[i] != max(lenlist):
#             while True:
#                 tempdatalist = getrealdata_url(starttimestamp, endtimestamp, stateid, [idlist[i]],sampleInterval, delaytime, advancetime, url1)
#                 if len(tempdatalist[0]) == max(lenlist):
#                     datalist[i] = tempdatalist[0]
#                     break
#     return datalist

# 检查每个id读的数据长度是否一致,读十次，如果不行就不再读了
def check_realdata(datalist, starttimestamp, endtimestamp, stateid, idlist, sampleInterval, delaytime, advancetime, url1):
    lenlist = []
    for i in range(len(datalist)):
        templen = len(datalist[i])
        lenlist.append(templen)
    lenlist=np.array(lenlist)
    for i in range(len(datalist)):
        readnum = 0
        if lenlist[i] != max(lenlist):
            while True:
                tempdatalist = getrealdata_url(starttimestamp, endtimestamp, stateid, [idlist[i]],sampleInterval, delaytime, advancetime, url1)
                if len(tempdatalist[0]) == max(lenlist):
                    datalist[i] = tempdatalist[0]
                    break
                readnum = readnum +1
                if readnum == 10:
                    datalist = []
                    print('无法正常读取数据！！！')
                    break
    return datalist

# 删除指定时间段的数据
def delete_databytime(inputdata,starttime,endtime):
    starttimestamp = strtotimestamp(starttime)
    endtimestamp = strtotimestamp(endtime)
    fin_inputdata = []
    for i in range(len(inputdata)):
        fin_inputdata.append([])
        for j in range(len(inputdata[0])):
            temptime = inputdata[0][j]
            temptimestamp = strtotimestamp(temptime)
            if temptimestamp > starttimestamp and temptimestamp < endtimestamp:
                continue
            fin_inputdata[i].append(inputdata[i][j])
    return fin_inputdata

# 发电态数据筛选,功率低于370的删掉
def delete_littlepowerdata(inputdata,outputdata):
    fin_inputdata = []
    fin_outputdata = []
    for i in range(len(inputdata)):
        fin_inputdata.append([])
        for j in range(len(inputdata[1])):
            if (abs(inputdata[1][j])<370):
                continue
            fin_inputdata[i].append(inputdata[i][j])
    for i in range(len(outputdata)):
        fin_outputdata.append([])
        for j in range(len(inputdata[1])):
            if (abs(inputdata[1][j]) < 370):
                continue
            fin_outputdata[i].append(outputdata[i][j])
    return fin_inputdata,fin_outputdata

# 找出列表大于均值加三倍标准差的点的索引
def find_3std(datalist):
    datalist = np.array(datalist)
    len1 = len(datalist)
    mean1 = datalist.mean()
    std1 = datalist.std()
    peaks = []
    for i in range(len1):
        if datalist[i] > mean1 + 3*std1 :
            peaks.append(i)
    return peaks

# 删除输出项中的离群点
# def delete_outlier(inputlist, outputlist, row_num):
#     peaks = find_3std(outputlist[row_num])
#     if len(peaks) == 0:
#         return inputlist,outputlist
#     peaks= np.array(peaks)
#     len1 = len(outputlist[row_num])
#     for i in range(len1):
#         temp = len1 - i -1
#         if temp in peaks:
#             for j in range(len(inputlist)):
#                 inputlist[j].pop(temp)
#             for k in range(len(outputlist)):
#                 outputlist[k].pop(temp)
#     return inputlist,outputlist

def delete_outlier(inputlist, outputlist, row_num):
    peaks = find_3std(outputlist[row_num])
    if len(peaks) == 0:
        return inputlist,outputlist
    peaks= np.array(peaks)
    len1 = len(outputlist[row_num])
    copy_inputlist = copy.deepcopy(inputlist)
    copy_outputlist = copy.deepcopy(outputlist)
    for i in range(len1):
        temp = len1 - i -1
        if temp in peaks:
            for j in range(len(copy_inputlist)):
                copy_inputlist[j].pop(temp)
            for k in range(len(copy_outputlist)):
                copy_outputlist[k].pop(temp)
    return copy_inputlist,copy_outputlist

# 删除输出项中的离群点
def delete_outlier1(inputlist, outputlist):
    peaks = find_3std(outputlist)
    if len(peaks) == 0:
        return inputlist,outputlist
    peaks= np.array(peaks)
    len1 = len(outputlist)
    copy_inputlist = copy.deepcopy(inputlist)
    copy_outputlist = copy.deepcopy(outputlist)
    for i in range(len1):
        temp = len1 - i -1
        if temp in peaks:
            for j in range(len(copy_inputlist)):
                copy_inputlist[j].pop(temp)
            copy_outputlist.pop(temp)
    return copy_inputlist,copy_outputlist

# 整理数据，第一行为时间，每一行为通道数据
def deal4Ddata(inputdata,outputdata):
    fin_inputdata = []
    fin_outputdata = []
    fin_inputdata.append([])
    fin_outputdata.append([])
    for i in range(len(inputdata)):
        fin_inputdata.append([])
        for j in range(len(inputdata[i])):
            for k in range(len(inputdata[i][j])):
                if i == 0:
                    fin_inputdata[0].append(inputdata[i][j][k][0])
                fin_inputdata[i+1].append(inputdata[i][j][k][1])
    for i in range(len(outputdata)):
        fin_outputdata.append([])
        for j in range(len(outputdata[i])):
            for k in range(len(outputdata[i][j])):
                if i == 0:
                    fin_outputdata[0].append(outputdata[i][j][k][0])
                fin_outputdata[i+1].append(outputdata[i][j][k][1])
    return fin_inputdata,fin_outputdata

# 整理三维数据，第一行为时间，每一行为通道数据
def deal3Ddata(inputdata, outputdata):
    fin_inputdata = []
    fin_outputdata = []
    fin_inputdata.append([])
    fin_outputdata.append([])
    for i in range(len(inputdata)):
        fin_inputdata.append([])
        for j in range(len(inputdata[i])):
            if i == 0:
                fin_inputdata[0].append(inputdata[i][j][0])
            fin_inputdata[i + 1].append(inputdata[i][j][1])
    for i in range(len(outputdata)):
        fin_outputdata.append([])
        for j in range(len(outputdata[i])):
            if i == 0:
                fin_outputdata[0].append(outputdata[i][j][0])
            fin_outputdata[i + 1].append(outputdata[i][j][1])
    return fin_inputdata, fin_outputdata

#  按照标幺值数据归一化
def per_unit(datalist,perval_list):
    result_list =[]
    for i in range(len(datalist)):
        if i ==0:
            # result_list.append(datalist[i])
            continue
        maxval = perval_list[i-1]
        templist = np.array(datalist[i])
        templist = abs(templist)
        templist = templist/maxval
        result_list.append(templist)
    return result_list

# 处理劣化序列，将其按运行时间,将每次运行过程做成一列样本
def deterlist_byruntime(detertime, deter_runtime, deterlist, start_runtime):
    result_deterlist = []
    result_time = []
    templist = []
    for i in range(len(deter_runtime)):
        if i == 0:
            templist.append(deterlist[i])
            result_time.append(detertime[i])
            continue
        if  deter_runtime[i] != start_runtime:
            templist.append(deterlist[i])
        elif deter_runtime[i] == start_runtime:
            result_time.append(detertime[i])
            result_deterlist.append(templist)
            templist = []
            templist.append(deterlist[i])
        if i == len(deter_runtime)-1:
            result_deterlist.append(templist)
    return result_deterlist,result_time

def get_listrow(row,list1):
    b = []
    b = [x[row] for x in  list1]
    return  b

def steady_deter_datalist(float_result,bool_result):
    stateflag = 0
    timelist1 = []; timelist2 = []; steady_list = []
    if(len(float_result)==0):
        return steady_list
    for i in range(len(bool_result)):
        if i == len(bool_result) - 1 and stateflag == 0 and bool_result[i][1] == 1:
            continue
        elif i == len(bool_result) - 1 and stateflag == 1 and bool_result[i][1] == 1:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] == 1 and stateflag == 0:
            stateflag = 1
            timelist1.append(bool_result[i][0])
        elif bool_result[i][1] == 0 and stateflag == 1:
            stateflag = 0
            timelist1.append(bool_result[i][0])
    #     取开机后一小时到关机前10分钟的稳态数据的平均值
    tdim = int(len(timelist1) / 2)
    for i in range(tdim):
        temptime = timelist1[2 * i]
        temptime = temptime + 60 * 60
        if temptime > timelist1[2 * i + 1] - 600:
            continue
        else:
            timelist2.append(temptime)
            temptime = timelist1[2 * i + 1] - 600
            timelist2.append(temptime)
    if len(timelist2) == 0:
        return steady_list
    # 得到时间对应的索引
    time_index = []
    for i in range(len(timelist2)):
        temp_index = get_index(float_result,timelist2[i])
        time_index.append(temp_index)
    dim = int(len(time_index) / 2)
    for i in range(dim):
        start_index = time_index[2 * i]
        end_index = time_index[2 * i + 1]
        sum_value = 0
        aver_value = 0
        j = 0
        if start_index == end_index:
            aver_value = float_result[start_index][1]
        else:
            for j in range(start_index, end_index):
                sum_value = sum_value + float_result[j][1]
            aver_value = sum_value / (end_index - start_index)
        start_time = timelist2[2 * i]
        # local_time = time.localtime(start_time)
        # local_timesd = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        # steady_list.append([local_timesd, aver_value])
        steady_list.append([start_time, aver_value])
    return steady_list


#   获取历史抽水、发电下稳态健康模型数据
def get_steady_health_hisdata(host, user, password, bool_port, float_port, pump_state,power_state, datalist,
                     year, month, sampleInterval):
    data_pump = []; data_power = []; result_pump = []; result_power = [];
    for index in range(len(datalist)):
        data_pump.append([])
        data_power.append([])
    for i in range(len(datalist)):
        tempdata_pump = [];tempdata_power = []; temp_pump = []; temp_power = []
        pump_time = 0;power_time = 0
        for j in range(len(year)):
            for k in range(len(month[j])):
                y = year[j]; m = month[j][k]
                pump_bool_result = read_bool_data(host, user, password, bool_port,pump_state,y, m)
                power_bool_result = read_bool_data(host, user, password, bool_port,power_state,y, m)
                float_result = read_float_data(host, user, password, float_port, datalist[i] ,y,m)
                [tempdata_pump,temp_pumptime] = steady_health_datalist(float_result,pump_bool_result,sampleInterval)
                [tempdata_power,temp_powertime] = steady_health_datalist(float_result,power_bool_result,sampleInterval)
                data_pump[i] = data_pump[i] + tempdata_pump
                data_power[i] = data_power[i] + tempdata_power
                pump_time = pump_time +temp_pumptime
                power_time = power_time + temp_powertime
        temp_pump = get_listrow(1,data_pump[i])
        temp_power = get_listrow(1,data_power[i])
        result_pump.append(temp_pump)
        result_power.append(temp_power)
    return result_pump, result_power,pump_time,power_time

# 获取历史抽水、发电下稳态劣化模型数据
def get_steady_deter_hisdata(host, user, password, bool_port, float_port, pump_state,power_state, datalist,
                     year, month):
    data_pump = []; data_power = []; result_pump = []; result_power = [];
    all_resultpump = [];all_resultpower =[]
    for index in range(len(datalist)):
        data_pump.append([])
        data_power.append([])
    for i in range(len(datalist)):
        tempdata_pump = [];tempdata_power = []; temp_pump = []; temp_power = []
        for j in range(len(year)):
            for k in range(len(month[j])):
                y = year[j]; m = month[j][k]
                pump_bool_result = read_bool_data(host, user, password, bool_port,pump_state,y, m)
                power_bool_result = read_bool_data(host, user, password, bool_port,power_state,y, m)
                float_result = read_float_data(host, user, password, float_port, datalist[i] ,y,m)
                tempdata_pump = steady_deter_datalist(float_result,pump_bool_result)
                tempdata_power = steady_deter_datalist(float_result,power_bool_result)
                data_pump[i] = data_pump[i] + tempdata_pump
                data_power[i] = data_power[i] + tempdata_power
        temp_pump = get_listrow(1,data_pump[i])
        temp_power = get_listrow(1,data_power[i])
        all_resultpump.append(data_pump[i])
        all_resultpower.append(data_power[i])
        result_pump.append(temp_pump)
        result_power.append(temp_power)
    return result_pump, result_power,all_resultpump,all_resultpower

def maponezero(data, direction="normal", maxmin=None):
    if direction == "normal":
        maxval = np.max(data)
        minval = np.min(data)
        data = (data - minval) / (maxval - minval)
        return [data, [maxval, minval]]
    if direction == "apply":
        maxval = maxmin[0]
        minval = maxmin[1]
        data = (data - minval) / (maxval - minval)
        return data
    if direction == "reverse":
        maxval = maxmin[0]
        minval = maxmin[1]
        data = data * (maxval - minval) + minval
        return data

# 数据归一化
def healthydata_normalizaton(ini_data):
    #  80%用来训练、数据归一化
    ini_data = np.array(ini_data)
    per = int(ini_data.shape[1] * 0.8)
    x_train0 = ini_data[:,0:per]
    x_test0 = ini_data[:,per:]
    x_train1 = []; x_test1 = []; x_maxmin1 = []
    for i in range(x_train0.shape[0]):
         x_traini = []; x_maxmini = []
         x_traini = x_train0[i, :]
         [x_traini, x_maxmini] = maponezero(x_traini)
         x_train1.append(x_traini)
         x_maxmin1.append(x_maxmini)
    for i in range(x_test0.shape[0]):
        x_testi = []; x_testi = x_test0[i, :]
        x_testi = maponezero(x_testi, 'apply', x_maxmin1[i])
        x_test1.append(x_testi)
    return x_train1,x_test1,x_maxmin1

# 数据随机，数据归一化
def healthydata_normalizaton_random(ini_inputdata,ini_outputdata):
    #  80%用来训练、数据归一化
    ini_inputdata = np.array(ini_inputdata)
    ini_outputdata = np.array(ini_outputdata)
    per = int(ini_inputdata.shape[1] * 0.8)
    r = np.arange(ini_inputdata.shape[1])
    np.random.shuffle(r)
    x_train0 = ini_inputdata[:, r[0:per]]
    y_train0 = ini_outputdata[:, r[0:per]]
    x_test0 = ini_inputdata[:, r[per:]]
    y_test0 = ini_outputdata[:, r[per:]]
    x_train1 = []; x_test1 = []; x_maxmin1 = []
    y_train1 = []; y_test1 = []; y_maxmin1 = []
    for i in range(x_train0.shape[0]):
         x_traini = []; x_maxmini = []
         x_traini = x_train0[i, :]
         [x_traini, x_maxmini] = maponezero(x_traini)
         x_train1.append(x_traini)
         x_maxmin1.append(x_maxmini)
    for i in range(x_test0.shape[0]):
        x_testi = []; x_testi = x_test0[i, :]
        x_testi = maponezero(x_testi, 'apply', x_maxmin1[i])
        x_test1.append(x_testi)
    for i in range(y_train0.shape[0]):
         y_traini = []; y_maxmini = []
         y_traini = y_train0[i, :]
         [y_traini, y_maxmini] = maponezero(y_traini)
         y_train1.append(y_traini)
         y_maxmin1.append(y_maxmini)
    for i in range(y_test0.shape[0]):
        y_testi = []; y_testi = y_test0[i, :]
        y_testi = maponezero(y_testi, 'apply', y_maxmin1[i])
        y_test1.append(y_testi)
    return x_train1,x_test1,x_maxmin1,y_train1,y_test1,y_maxmin1

# 输出加权
def output_weight(outputdata):
    outputdata = np.array(outputdata)
    output_data = outputdata.sum(0)/outputdata.shape[0]
    return output_data


# 写一个LossHistory类，保存loss和acc
class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch': [], 'epoch': []}
        self.accuracy = {'batch': [], 'epoch': []}
        self.val_loss = {'batch': [], 'epoch': []}
        self.val_acc = {'batch': [], 'epoch': []}

    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.accuracy['batch'].append(logs.get('acc'))
        self.val_loss['batch'].append(logs.get('val_loss'))
        self.val_acc['batch'].append(logs.get('val_acc'))

    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.accuracy['epoch'].append(logs.get('acc'))
        self.val_loss['epoch'].append(logs.get('val_loss'))
        self.val_acc['epoch'].append(logs.get('val_acc'))

    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))
        plt.figure()
        # acc
        plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        # loss
        plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':
            # val_acc
            plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            # val_loss
            plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)
        plt.xlabel(loss_type)
        plt.ylabel('acc-loss')
        plt.legend(loc="upper right")
        plt.show()

# 建立健康状态模型
def build_healthy_model(x_train, x_test, y_train, y_test, epochs, batch_size,
                        validation_split, savepath,unit, modelnum, modeltime):
    input_shape = np.array(x_train).shape[1]
    # output_shape = np.array(y_train).shape[1]
    output_shape = 1
    fittime = 0
    #  搭建模型
    while True:
        K.clear_session()
        tf.reset_default_graph()
        data_input = Input(shape=(input_shape,), name='train_input')
        # layer1 = Dense(256, activation='relu')(data_input)
        layer1 = Dense(128,activation='relu')(data_input)
        # layer1 = Dropout(0.2)(layer1)
        # layer1 = Dense(64, activation='relu')(data_input)
        layer1 = Dropout(0.2)(layer1)
        layer1 = Dense(64, activation='relu')(layer1)
        layer1 = Dense(32, activation='relu')(layer1)
        # layer1 = Dense(32,activation='relu')(data_input)
        # layer1 = Dropout(0.2)(layer1)
        layer1 = Dense(16, activation='relu')(layer1)
        layer1 = Dense(8, activation='relu')(layer1)
        layer1 = Dense(4, activation='relu')(layer1)
        layer1 = Dense(2, activation='relu')(layer1)
        data_output = Dense(output_shape, activation='linear')(layer1)
        model1 = Model(inputs=data_input, outputs=data_output)
        model1.compile(loss='mse', optimizer='rmsprop')
        # model1.compile(loss='mse', optimizer='adam')
        # history = LossHistory()
        #  训练模型
        # model1.fit(x =x_train,y = y_train,epochs = epochs, verbose=0,
        #            batch_size= batch_size,validation_split= validation_split,callbacks=[history])
        model1.fit(x=x_train, y=y_train, epochs=epochs, verbose=0,
                   batch_size=batch_size, validation_split=validation_split)
        # 对训练集和测试集进行预测
        predict_train = model1.predict(x_train)
        predict_train = np.reshape(predict_train, (predict_train.shape[0],))
        predict_test = model1.predict(x_test)
        predict_test = np.reshape(predict_test, (predict_test.shape[0],))
        # 计算相对平均误差
        # MAPE_train = np.sum(np.abs(y_train - predict_train) / y_train) / len(y_train)
        # MAPE_test = np.sum(np.abs(y_test - predict_test) / y_test) / len(y_test)
        print("fittime= ",fittime)
        fittime = fittime +1
        flag = allone(predict_train)
        # if MAPE_train < 0.10 or fittime > 2:
        #     break
        if flag==0:
            break
    # history.loss_plot('epoch')
    # 保存模型
    model1.save(savepath + '/healthymodel' +str(unit) + str(modelnum) +'_'+ str(modeltime) + '.h5')
    return model1

# 建立劣化预测模型
def build_determodel_lstm(x_train, y_train, epochs, batch_size, validation_split, savepath, modelnum, modeltime):
    input_shape = np.array(x_train).shape[1]
    fittime = 0
    while True:
        K.clear_session()
        tf.reset_default_graph()
        ipt = Input(shape=(input_shape, 1), name='train_input')
        # lstm = LSTM(units=256, return_sequences=False)(ipt)
        # ds = Dense(128, activation='relu')(lstm)
        # ds = Dense(64, activation='relu')(ds)
        # ds = Dense(32, activation='relu')(ds)
        # ds = Dense(16, activation='relu')(ds)
        # ds = Dense(8, activation='relu')(ds)
        # ds = Dense(4, activation='relu')(ds)
        # opt = Dense(1, activation='linear')(ds)
        # gru = GRU(128, activation='relu', return_sequences=True)(ipt)
        # gru = GRU(64, activation='relu', return_sequences=True)(ipt)
        gru = GRU(32, activation='relu', return_sequences=True)(ipt)
        gru = GRU(16, activation='relu', return_sequences=True)(gru)
        gru = GRU(8, activation='relu', return_sequences=False)(gru)
        # ds = Dense(16, activation='relu')(gru)
        # ds = Dense(8, activation='relu')(ds)
        ds = Dense(4, activation='relu')(gru)
        opt = Dense(1, activation='linear')(ds)
        model = Model(inputs=ipt, outputs=opt)
        model.compile(loss='mse', optimizer='rmsprop')
        history = LossHistory()
        # 训练模型
        model.fit(x=x_train, y=y_train, epochs=epochs,  verbose=0, batch_size=batch_size,
                  validation_split=validation_split, callbacks=[history])
        # 训练集做预测
        print("fittime= ", fittime)
        fittime = fittime + 1
        predict_train = model.predict(x_train)
        predict_train = np.reshape(predict_train, (predict_train.shape[0],))
        flag = allone(predict_train)
        if flag == 0:
            break
    history.loss_plot('epoch')
    # 保存模型
    model.save(savepath + '/determodel' + str(modelnum) + str(modeltime) + '.h5')
    return model

# 劣化模型预测
def determodel_predict(determodel,x_train,x_test):
    # 对训练集和测试集进行预测
    predict_train = determodel.predict(x_train)
    predict_train = np.reshape(predict_train, (predict_train.shape[0],))
    predict_test = determodel.predict(x_test)
    predict_test = np.reshape(predict_test, (predict_test.shape[0],))
    return predict_train,predict_test

# 判断数组是否都为一个值
def allone(arraylist):
    flag = 1
    data1 = arraylist[0]
    for i in range(len(arraylist)):
        if flag == 0:
            break
        if arraylist[i] == data1:
            flag = 1
        else:
            flag =0
    return flag

# 计算健康状态模型预测结果，及误差
def healthymodel_predict(healthymodel,x_train,x_test,y_train,y_test,model_num):
    # 对训练集和测试集进行预测
    predict_train = healthymodel.predict(x_train)
    predict_train = np.reshape(predict_train, (predict_train.shape[0],))
    predict_test = healthymodel.predict(x_test)
    predict_test = np.reshape(predict_test, (predict_test.shape[0],))
    # 计算相对平均误差
    MAPE_train = np.sum(np.abs(y_train - predict_train) / y_train) / len(y_train)
    MAPE_test = np.sum(np.abs(y_test - predict_test) / y_test) / len(y_test)
    print(str(model_num)+'MAPE_train1', MAPE_train, '\n', str(model_num)+'MAPE_test1', MAPE_test)
    # 计算均方根误差
    RMSE_train = np.sqrt(np.sum((y_train - predict_train) ** 2) / len(y_train))
    RMSE_test = np.sqrt(np.sum((y_test - predict_test) ** 2) / len(y_test))
    print(str(model_num)+'RMSE_train1', RMSE_train, '\n', str(model_num)+'RMSE_test1', RMSE_test)
    return predict_train, predict_test,MAPE_train,MAPE_test,RMSE_train,RMSE_test

# 计算健康状态模型预测结果，反归一化及误差
def healthymodel_predict1(healthymodel, x_train, x_test, Y_train, Y_test, maxmin,model_num):
    # 对训练集和测试集进行预测
    predict_train = healthymodel.predict(x_train)
    predict_train = np.reshape(predict_train, (predict_train.shape[0],))
    predict_test = healthymodel.predict(x_test)
    predict_test = np.reshape(predict_test, (predict_test.shape[0],))
    # 反归一化
    # Predict_train = minmax_scaling(predict_train,'reverse',maxmin)
    # Predict_test = minmax_scaling(predict_test,'reverse',maxmin)
    Predict_train = predict_train*maxmin
    Predict_test = predict_test*maxmin
    # 计算相对平均误差
    MAPE_train = np.sum(np.abs((Y_train - Predict_train) / Y_train)) / len(Y_train)
    MAPE_test = np.sum(np.abs((Y_test - Predict_test) / Y_test)) / len(Y_test)
    print(str(model_num)+'MAPE_train1', MAPE_train, '\n', str(model_num)+'MAPE_test1', MAPE_test)
    # 计算均方根误差
    RMSE_train = np.sqrt(np.sum((Y_train - Predict_train) ** 2) / len(Y_train))
    RMSE_test = np.sqrt(np.sum((Y_test - Predict_test) ** 2) / len(Y_test))
    print(str(model_num)+'RMSE_train1', RMSE_train, '\n', str(model_num)+'RMSE_test1', RMSE_test)
    return Predict_train, Predict_test,MAPE_train,MAPE_test,RMSE_train,RMSE_test

# 健康状态模型预测结果绘图
def plot_healthymodelresult(y_train, y_test, predict_train, predict_test, model_name,up_threshold):
    plt.figure(str(model_name) + '训练集', facecolor='white')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(y_train, 'r', label='真实值')
    plt.plot(predict_train, 'g', label='预测值')
    plt.xlabel("时间", fontsize=20)
    plt.ylabel(str(model_name), fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    new_ticks = np.linspace(0, up_threshold, 11)
    plt.yticks(new_ticks)
    font1 = {'size': 20, }
    plt.legend(prop=font1)

    plt.figure(str(model_name) + '测试集 ', facecolor='white')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(y_test, 'r', label='真实值')
    plt.plot(predict_test, 'g', label='预测值')
    plt.xlabel("时间", fontsize=20)
    plt.ylabel(str(model_name), fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    new_ticks = np.linspace(0, up_threshold, 11)
    plt.yticks(new_ticks)
    font1 = {'size': 20, }
    plt.legend(prop=font1)
    plt.show()

# 绘制劣化度预测曲线
def plot_detertrend(true_data,predict_data,timelist,figure_name):
    time_axis = [datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in timelist]
    plt.figure(str(figure_name), facecolor='white')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(time_axis,true_data, '*r', label='真实值')
    plt.plot(time_axis,predict_data, '*g', label='预测值')
    plt.xlabel("时间", fontsize=20)
    plt.ylabel("劣化度", fontsize=20)
    new_ticks = np.linspace(-1, 1, 11)
    plt.yticks(new_ticks)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    font1 = {'size': 20, }
    plt.legend(prop=font1)
    plt.show()

def plot_detertrend1(true_data,predict_data,timelist,figure_name):
    time_axis = [datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in timelist]
    plt.figure(str(figure_name), facecolor='white')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(time_axis,true_data, '-*r', label='真实值')
    plt.plot(time_axis,predict_data, '-*g', label='预测值')
    plt.xlabel("时间", fontsize=20)
    plt.ylabel("劣化度", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    font1 = {'size': 20, }
    plt.legend(prop=font1)
    plt.show()

def deterdata_normalization(ini_data,maxmin):
    result = []
    ini_data = np.array(ini_data)
    for i in range(ini_data.shape[0]):
        ini_datai = [];
        ini_datai = ini_data[i, :]
        ini_datai = maponezero(ini_datai, 'apply', maxmin[i])
        result.append(ini_datai)
    return result

# 构造劣化序列,分母为基准值
def build_deterlist(healthymodel, deterinput, deteroutput,deter_standard):
    # 预测
    predict_data = healthymodel.predict(deterinput)
    predict_data = np.array(predict_data)
    predict_data = np.reshape(predict_data, (predict_data.shape[0],))
    # 反归一化
    Deteroutput = deteroutput*deter_standard
    Predict_data = predict_data*deter_standard
    # 计算劣化度
    deter_data = (Deteroutput - Predict_data) / deter_standard
    # 相对劣化度
    deter_data1 = (Deteroutput - Predict_data) / Predict_data
    # 归一劣化度
    deter_data2 = (Deteroutput - Predict_data) /(deter_standard -Predict_data)
    return deter_data,deter_data1,deter_data2

# def build_deterlist(healthymodel, deterinput, deteroutput):
#     # 预测
#     predict_data = healthymodel.predict(deterinput)
#     predict_data = np.array(predict_data)
#     predict_data = np.reshape(predict_data, (predict_data.shape[0],))
#     # deter_data = abs((deteroutput - predict_data) / predict_data)
#     deter_data = (deteroutput - predict_data) / predict_data
#     return deter_data

# 画图带时间
def plot_withtime(timelist,deterlist,figure_name,label_name):
    time_axis = [datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in timelist]
    plt.figure( str(figure_name), facecolor='white')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(time_axis,deterlist, '*r', label=str(label_name))
    plt.xlabel("时间", fontsize=20)
    plt.ylabel("劣化度", fontsize=20)
    # plt.xticks(datetime.datetime.strptime('2018-01-02','%Y-%m-%d'), datetime.datetime.strptime('2018-02-02','%Y-%m-%d') ,
    #            datetime.datetime.strptime('2018-03-02','%Y-%m-%d'),datetime.datetime.strptime('2018-04-02','%Y-%m-%d'),
    #            datetime.datetime.strptime('2018-05-02','%Y-%m-%d') )
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    new_ticks = np.linspace(-1, 1, 11)
    plt.yticks(new_ticks)
    font1 = {'size': 20, }
    plt.legend(prop=font1)
    plt.show()

# 劣化序列画图
def plot_deterlist(deterlist,figure_name):
    plt.figure( str(figure_name), facecolor='white')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(deterlist, 'r', label='真实值')
    plt.xlabel("时间", fontsize=20)
    plt.ylabel("劣化度", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    font1 = {'size': 20, }
    plt.legend(prop=font1)
    plt.show()

# 构造劣化阶段健康模型输出与实际值表
def build_healout_table(host, user, password, port):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    creatsql = "CREATE TABLE if not exists tre_healout(unit int not null,id int not null,time int not null," \
               "healout float not null,realval float not null,primary key(unit,id,time)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    try:
        cursor.execute(creatsql)
    except:
        print('unable to build healout table!')
    conn.close()

# 健康模型输出序列存储
def healout_starage(host, user, password, port, unit,id,timelist,healout_list,realval_list):
    if not isinstance(timelist,list):
        timelist = timelist.tolist()
    if not isinstance(healout_list,list):
        healout_list = healout_list.tolist()
    if not isinstance(realval_list,list):
        realval_list = realval_list.tolist()
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    insertsql = "INSERT INTO tre_healout(unit,id,time,healout,realval) VALUES(%s,%s,%s,%s,%s)"
    for i in range(len(timelist)):
        time1 = timelist[i]
        healout = healout_list[i]
        realval = realval_list[i]
        try:
            cursor.execute(insertsql, (unit,id,time1,healout,realval))
            conn.commit()
        except:
            print('unable to insert data into healout!')
    conn.close()

# 构造劣化阈值表
def build_deterthreshold_table(host, user, password, port):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    creatsql = "CREATE TABLE if not exists tre_deter_threshold(unit int not null,id int not null,name varchar(100) not null," \
               "val float not null,relative_ids varchar(100),primary key(unit,id)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    try:
        cursor.execute(creatsql)
    except:
        print('unable to build deter_threshold !')
    conn.close()

# 构造历史劣化序列表
def build_deterdata_table(host, user, password, port):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    creatsql = "CREATE TABLE if not exists tre_deterdata(unit int not null,id int not null," \
               "time int not null,runtime int not null,deter float not null,version int not null," \
               "primary key(unit,id,runtime,version)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    try:
        cursor.execute(creatsql)
    except:
        print('unable to build deterdata table !')
    conn.close()

# 构造预测劣化序列表
def build_deterpre_table(host, user, password, port):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    creatsql = "CREATE TABLE if not exists tre_deterpre(unit int not null,id int not null," \
               "pretime int not null,predeter float not null,threshold float not null,version int not null," \
               "primary key(unit,id,pretime,version)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    try:
        cursor.execute(creatsql)
    except:
        print('unable to build deterpre table !')
    conn.close()

# 历史劣化序列存储
def deterdata_starage(host, user, password, port, unit,id, hisdeter_time, start_runtime,hisdeter_data,version):
    start_runtime = int(start_runtime)
    version = int(version)
    if not isinstance(hisdeter_data,list):
        hisdeter_data = hisdeter_data.tolist()
    if not isinstance(hisdeter_time,list):
        hisdeter_time = hisdeter_time.tolist()
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    insertsql = "INSERT INTO tre_deterdata(unit,id,time,runtime,deter,version) VALUES(%s,%s,%s,%s,%s,%s)"
    try:
        for i in range(len(hisdeter_data)):
            time1 = hisdeter_time[i]
            runtime = start_runtime + i
            deter = hisdeter_data[i]
            deter = float(deter)
            cursor.execute(insertsql, (unit,id,time1,runtime,deter,version))
            conn.commit()
        print('历史数据存储！', str(unit) + str(id))
    except:
        print('unable to insert into deterdata table !')
    conn.close()
    if id > 30:
        posttrend(host,user,password,port,unit,id,start_runtime,hisdeter_data,ip_port='23.49.171.53:8085')

# 将数据集划分为训练集和测试集，和最后几步预测集
def division_dataset(dataset,timesteps,pre_steps):
    result = []
    for index in range(len(dataset) - timesteps - pre_steps + 1):
        result.append(dataset[index:index + timesteps + pre_steps])
    result = np.array(result)
    # 划分训练集和测试集，并添加预测集
    row = round(0.8 * result.shape[0])
    x_train = result[:int(row), :timesteps]
    y_train = result[:int(row), -1]
    x_test = result[int(row):, :timesteps]
    y_test = result[int(row):, -1]
    # 新增预测集
    temp_test = []
    for i in range(pre_steps):
        temp_test.append(result[-1, i + 1: i + timesteps + 1])
    temp_test = np.array(temp_test)
    x_pre_test = np.concatenate((x_test, temp_test))
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    x_pre_test = np.reshape(x_pre_test, (x_pre_test.shape[0], x_pre_test.shape[1], 1))
    return x_train, x_test, y_train, y_test, x_pre_test

def vmd_decomposition(data, pre_seq_len=0, pre_step=0, vmd_k=0, vmd_alpha=1000):
    print('> vmd processing...')
    # VMD分解 多步单点
    alpha = vmd_alpha  # moderate bandwidth constraint
    tau = 0  # noise-tolerance (no strict fidelity enforcement)
    K = vmd_k  # 3modes
    DC = 0  # no DC part imposed
    init = 1  # initialize omegas uniformly
    tol = 1e-7
    REI = np.inf
    tauo = 0
    for tau in [x / 10 for x in range(11)]:
        [u, u_hat, omega] = vmd.vmd(data, alpha, tau, K, DC, init, tol)
        temp = np.sqrt(np.sum((np.sum(u, 0) - data) ** 2, 0) / len(data))  # sum(a,0)才等于matlab中的sum
        if temp < REI:
            REI = temp
            tauo = tau
    tau = tauo
    [u, u_hat, omega] = vmd.vmd(data, alpha, tau, K, DC, init, tol)
    print('> vmd processed...')
    # 处理数据
    x_trains = []
    y_trains = []
    x_tests = []
    y_tests = []
    x_pre_tests = []
    for i in range(vmd_k + 1):
        result = []
        if i < vmd_k:
            seq = u[i]
        else:
            seq = data
        for index in range(len(seq) - pre_seq_len - pre_step + 1):
            result.append(seq[index:index + pre_seq_len + pre_step])  # 每一次添加一个列表作为元素，表示矩阵的一行0;12+4
        result = np.array(result)  # 用numpy对其进行矩阵化
        # 划分训练集和测试集，并添加预测集
        row = round(0.8 * result.shape[0])
        print('vmd_row   ',row)
        x_train = result[:int(row), :pre_seq_len]
        y_train = result[:int(row), -1]
        x_test = result[int(row):, :pre_seq_len]
        y_test = result[int(row):, -1]
        # 新增预测集
        temp_test = []
        for i in range(pre_step):
            temp_test.append(result[-1, i + 1: i + pre_seq_len + 1])
        temp_test = np.array(temp_test)
        x_pre_test = np.concatenate((x_test, temp_test))
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        x_pre_test = np.reshape(x_pre_test, (x_pre_test.shape[0],x_pre_test.shape[1],1))
        x_trains.append(x_train)
        y_trains.append(y_train)
        x_tests.append(x_test)
        x_pre_tests.append(x_pre_test)
        y_tests.append(y_test)
    return [x_trains, y_trains, x_tests, y_tests,x_pre_tests]

# 计算mae,mape,rmse
def calerror(truelist,prelist):
    MAE = np.sum(np.abs(truelist - prelist)) / len(truelist)

    arrA = np.abs(truelist - prelist)
    arrB = truelist
    temp = np.divide(arrA, arrB, out=np.zeros_like(arrA, dtype=np.float64), where=arrB!=0)
    MAPE = np.sum(temp) / len(truelist)
    # MAPE = np.sum(np.abs((truelist - prelist) / truelist)) / len(truelist)
    RMSE = np.sqrt(np.sum((truelist - prelist) ** 2) / len(truelist))
    return MAE,MAPE,RMSE

#将序列滑动平均，k步取一次平均
def moving_average(datalist,k):
    if len(datalist) < k:
        return datalist
    resultlist =[]
    for i in range(len(datalist)-k):
        temp = sum(datalist[i:i+k])/k
        resultlist.append(temp)
    return resultlist

# 劣化预测模型(加入健康数据)
def deterlist_predictVMD(epochs, timesteps, pre_steps, vmd_k, vmd_alpha, health_deterdata, deter_data0, model_num):
    deter_data0 = np.array(deter_data0)
    all_data0 = np.concatenate((health_deterdata,deter_data0))
    all_data = moving_average(all_data0,5)
    if len(all_data) > 800:
        deter_data = all_data[-800:]
    else:
        deter_data = all_data
    # vmd分解的数据长度为偶数
    if (len(deter_data) % 2 == 0):
        deter_data = deter_data
    elif (len(deter_data) % 2 == 1):
        deter_data = deter_data[1:]
        flag = 1
    # vmd 分解
    [X_trains, Y_trains, X_tests, Y_tests, X_pre_tests] = vmd_decomposition(deter_data, pre_seq_len=timesteps,
                        pre_step=pre_steps, vmd_k=vmd_k, vmd_alpha=vmd_alpha)
    x_trains = []; y_trains = []
    x_tests = []; y_tests = []; x_pre_tests = []
    x_maxmins = []; y_maxmins = []
    # 归一化
    for k in range(vmd_k):
        [x_train, x_maxmin] = maponezero(X_trains[k])
        [y_train, y_maxmin] = maponezero(Y_trains[k])
        x_test = maponezero(X_tests[k], "apply", x_maxmin)
        x_pre_test = maponezero(X_pre_tests[k],"apply",x_maxmin)
        y_test = maponezero(Y_tests[k], "apply", y_maxmin)
        x_trains.append(x_train)
        y_trains.append(y_train)
        x_tests.append(x_test)
        x_pre_tests.append(x_pre_test)
        y_tests.append(y_test)
        x_maxmins.append(x_maxmin)
        y_maxmins.append(y_maxmin)
    y_trains_sum = 0
    y_tests_sum = 0
    predict_trains_sum = 0
    predict_tests_sum = 0
    predict_pre_tests_sum = 0
    for k in range(vmd_k):
        error_times = 0
        while True:
            # clear model data and state to avoid memory leak
            K.clear_session()
            tf.reset_default_graph()
            print('>compiling...', k)
            start_time = time.time()
            #   build model
            ipt = Input(shape=(timesteps, 1), name='train_input')
            lstm = LSTM(units=64, return_sequences=False)(ipt)
            # lstm = LSTM(units=64, return_sequences=True)(ipt)
            # lstm = LSTM(units=32, return_sequences=False)(lstm)
            ds = Dense(32, activation='relu')(lstm)
            ds = Dense(16, activation='relu')(ds)
            ds = Dense(8, activation='relu')(ds)
            ds = Dense(4, activation='relu')(ds)
            opt = Dense(1, activation='linear')(ds)
            model2 = Model(inputs=ipt, outputs=opt)
            model2.compile(loss='mse', optimizer='rmsprop')
            # train model
            model2.fit(x=x_trains[k], y=y_trains[k], epochs=epochs, verbose=0,
                       batch_size=64, validation_split=0.05)
            # predict model
            predict_trains = model2.predict(x_trains[k])
            predict_tests = model2.predict(x_tests[k])
            predict_pre_tests = model2.predict(x_pre_tests[k])
            predict_trains = np.reshape(predict_trains, (predict_trains.shape[0],))
            predict_tests = np.reshape(predict_tests, (predict_tests.shape[0],))
            predict_pre_tests = np.reshape(predict_pre_tests,(predict_pre_tests.shape[0],))
            #   反归一化
            predict_trains = maponezero(predict_trains, 'reverse', y_maxmins[k])
            predict_tests = maponezero(predict_tests, 'reverse', y_maxmins[k])
            predict_pre_tests = maponezero(predict_pre_tests, 'reverse',y_maxmins[k])
            MAE_trains = np.sum(np.abs(Y_trains[k] - predict_trains)) / len(Y_trains[k])
            MAE_tests = np.sum(np.abs(Y_tests[k] - predict_tests)) / len(Y_tests[k])

            MAPE_trains = np.sum(np.abs(Y_trains[k] - predict_trains) / Y_trains[k]) / len(Y_trains[k])
            MAPE_tests = np.sum(np.abs(Y_tests[k] - predict_tests) / Y_tests[k]) / len(Y_tests[k])
            #  print(Y_trains,'\n',Y_trains[k])
            if MAE_trains < 0.005 or error_times > 0:
                predict_trains_sum += predict_trains
                predict_tests_sum += predict_tests
                predict_pre_tests_sum += predict_pre_tests
                y_trains_sum += Y_trains[k]
                y_tests_sum += Y_tests[k]
                print('error_times:  ', error_times)
                print(str(model_num)+'mae_trains ' + str(k) + ': ', MAE_trains)
                print(str(model_num)+'mae_tests ' + str(k) + ': ', MAE_tests)
                print(str(model_num)+'are_trains ' + str(k) + ':', MAPE_trains)
                print(str(model_num)+'are_tests ' + str(k) + ':', MAPE_tests)
                plt.figure(str(model_num)+'train predict of imf' + str(k), facecolor='white')
                plt.plot(Y_trains[k], 'r', label='true data')
                plt.plot(predict_trains, 'g', label='predict data')
                plt.legend()
                plt.figure(str(model_num)+'test predict of imf' + str(k), facecolor='white')
                plt.plot(Y_tests[k], 'r', label='true data')
                plt.plot(predict_tests, 'g', label='predict data')
                plt.legend()
                break
            error_times += 1
            print('error_times:  ', error_times)
            print(str(model_num)+'mae_trains ' + str(k) + ': ', MAE_trains)
            print(str(model_num)+'mae_tests ' + str(k) + ': ', MAE_tests)
            print(str(model_num)+'are_trains ' + str(k) + ':', MAPE_trains)
            print(str(model_num)+'are_tests ' + str(k) + ':', MAPE_tests)
    print('Traing duration(s) :', time.time() - start_time)
    if len(deter_data0)>len(predict_pre_tests):
        y_test_data = deter_data[-len(predict_tests_sum):]
        deter_runtime = len(deter_data0) - len(predict_tests_sum)
        return predict_pre_tests_sum, y_test_data, deter_runtime,predict_tests_sum,predict_trains_sum,y_trains_sum
    else:
        # y_test_data = deter_data0
        y_test_data = deter_data[-len(deter_data0):]
        deter_runtime = 0
        return predict_pre_tests_sum[-len(deter_data0):], y_test_data, deter_runtime,predict_tests_sum,predict_trains_sum,y_trains_sum

def creat_model(input_len, output_len):
    ipt = Input(shape=(input_len, 1), name='train_input')
    lstm = LSTM(units=32, return_sequences=False)(ipt)
    ds = Dense(16, activation='relu')(lstm)
    # ds = Dropout(0.2)(ds)
    # ds = Dense(16, activation='relu')(ds)
    ds = Dense(8, activation='relu')(ds)
    ds = Dense(4, activation='relu')(ds)
    opt = Dense(output_len, activation='linear')(ds)
    return Model(inputs=ipt, outputs=opt)

def deterlist_predictVMD0(epochs, timesteps, pre_steps, vmd_k, vmd_alpha, deter_data0, model_num):
    deter_data0 = np.array(deter_data0)
    # vmd分解的数据长度为偶数
    if (len(deter_data0) % 2 == 0):
        deter_data = deter_data0
    elif (len(deter_data0) % 2 == 1):
        deter_data = deter_data0[1:]
    # vmd 分解
    [X_trains, Y_trains, X_tests, Y_tests, X_pre_tests] = vmd_decomposition(deter_data, pre_seq_len=timesteps,
                        pre_step=pre_steps, vmd_k=vmd_k, vmd_alpha=vmd_alpha)
    x_trains = []; y_trains = []
    x_tests = []; y_tests = []; x_pre_tests = []
    x_maxmins = []; y_maxmins = []
    # 归一化
    for k in range(vmd_k):
        [x_train, x_maxmin] = maponezero(X_trains[k])
        [y_train, y_maxmin] = maponezero(Y_trains[k])
        x_test = maponezero(X_tests[k], "apply", x_maxmin)
        x_pre_test = maponezero(X_pre_tests[k],"apply",x_maxmin)
        y_test = maponezero(Y_tests[k], "apply", y_maxmin)
        x_trains.append(x_train)
        y_trains.append(y_train)
        x_tests.append(x_test)
        x_pre_tests.append(x_pre_test)
        y_tests.append(y_test)
        x_maxmins.append(x_maxmin)
        y_maxmins.append(y_maxmin)
    y_trains_sum = 0
    y_tests_sum = 0
    predict_trains_sum = 0
    predict_tests_sum = 0
    predict_pre_tests_sum = 0
    for k in range(vmd_k):
        error_times = 0
        while True:
            # clear model data and state to avoid memory leak
            K.clear_session()
            tf.reset_default_graph()
            print('>Compiling...', k)
            #   build model
            # ipt = Input(shape=(timesteps, 1), name='train_input')
            # lstm = LSTM(units=32, return_sequences=False)(ipt)
            # ds = Dense(16, activation='relu')(lstm)
            # # ds = Dropout(0.2)(ds)
            # # ds = Dense(16, activation='relu')(ds)
            # ds = Dense(8, activation='relu')(ds)
            # ds = Dense(4, activation='relu')(ds)
            # opt = Dense(1, activation='linear')(ds)
            # model2 = Model(inputs=ipt, outputs=opt)
            model2 = creat_model(timesteps, 1)
            model2.compile(loss='mse', optimizer='rmsprop')
            # train model
            history = LossHistory()
            model2.fit(x=x_trains[k], y=y_trains[k], epochs=epochs, verbose=2,
                       batch_size=32, validation_split=0.05, callbacks=[history])
            # predict model
            predict_trains = model2.predict(x_trains[k])
            predict_tests = model2.predict(x_tests[k])
            predict_pre_tests = model2.predict(x_pre_tests[k])
            predict_trains = np.reshape(predict_trains, (predict_trains.shape[0],))
            predict_tests = np.reshape(predict_tests, (predict_tests.shape[0],))
            predict_pre_tests = np.reshape(predict_pre_tests,(predict_pre_tests.shape[0],))
            #   反归一化
            predict_trains = maponezero(predict_trains, 'reverse', y_maxmins[k])
            predict_tests = maponezero(predict_tests, 'reverse', y_maxmins[k])
            predict_pre_tests = maponezero(predict_pre_tests, 'reverse',y_maxmins[k])
            MAE_trains = np.sum(np.abs(Y_trains[k] - predict_trains)) / len(Y_trains[k])
            MAE_tests = np.sum(np.abs(Y_tests[k] - predict_tests)) / len(Y_tests[k])
            MAPE_trains = np.sum(np.abs((Y_trains[k] - predict_trains)/ Y_trains[k])) / len(Y_trains[k])
            MAPE_tests = np.sum(np.abs((Y_tests[k] - predict_tests) / Y_tests[k])) / len(Y_tests[k])
            flag = allone(predict_trains)
            if flag == 0:
                # history.loss_plot('epoch')
                predict_trains_sum += predict_trains
                predict_tests_sum += predict_tests
                predict_pre_tests_sum += predict_pre_tests
                y_trains_sum += Y_trains[k]
                y_tests_sum += Y_tests[k]
                # plt.figure(str(model_num)+'train predict of imf' + str(k), facecolor='white')
                # plt.plot(Y_trains[k], 'r', label='true data')
                # plt.plot(predict_trains, 'g', label='predict data')
                # plt.legend()
                # plt.figure(str(model_num)+'test predict of imf' + str(k), facecolor='white')
                # plt.plot(Y_tests[k], 'r', label='true data')
                # plt.plot(predict_tests, 'g', label='predict data')
                # plt.legend()
                break
            error_times += 1
            print('error_times:  ', error_times)
            print(str(model_num)+'mae_trains ' + str(k) + ': ', MAE_trains)
            print(str(model_num)+'mae_tests ' + str(k) + ': ', MAE_tests)
            print(str(model_num)+'are_trains ' + str(k) + ': ', MAPE_trains)
            print(str(model_num)+'are_tests ' + str(k) + ': ', MAPE_tests)
    y_test_data = deter_data[-len(predict_tests_sum):]
    # deter_runtime = len(deter_data0) - len(predict_tests_sum)
    y_train_data = deter_data[timesteps+pre_steps-1:-len(predict_tests_sum)]

    predict_pre_tests_sum = np.concatenate((predict_trains_sum,predict_pre_tests_sum))
    deter_runtime = len(deter_data0) - len(predict_trains_sum) -len(predict_tests_sum)

    return predict_pre_tests_sum, deter_runtime, y_test_data, predict_tests_sum, y_train_data, predict_trains_sum

# 保存预测结果
def deterpre_starage(host, user, password, port, unit, model_id, prestart_runtime, predeter, pre_steps, version):
    type = 1
    version = int(version)
    prestart_runtime = int(prestart_runtime)
    if not isinstance(predeter,list):
        predeter = predeter.tolist()
    [pre_threshold,modelname] = read_thresholdname(host, user, password, port, unit,model_id)
    equip = read_equipment(host,user,password,port,unit,model_id)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    insertdeterpre_sql = "INSERT INTO tre_deterpre(unit,id,pretime,predeter,threshold,version) VALUES(%s,%s,%s,%s,%s,%s)"
    insertwarn_sql = "insert into tre_warn(unit,id,type,time,name,warn,equip)values(%s,%s,%s,%s,%s,%s,%s)"
    flag = 0
    for i in range(len(predeter)):
        temp_predeter = predeter[i]
        temp_predeter = float(temp_predeter)
        warnsig = 0
        temp_time = prestart_runtime + i
        if temp_predeter > pre_threshold:
            flag = 1
            warnsig = 1
            warn_runtime = temp_time - pre_steps
            warn_time = get_warntime(host,user,password,port,unit,model_id,warn_runtime,version)
            try:
                cursor.execute(insertwarn_sql,(unit,model_id,type,warn_time,modelname,warnsig,equip))
                print("存入一个预警记录到tre_warn表")
            except:
                print("unable to insert into tre_warn table !")
            postforewarnhdy(host, user, password, port, unit, model_id,
                            modelname, warn_time, pre_threshold, temp_predeter, ip_port='23.49.171.53:8085')
            postforewarnnr(host, user, password, port, unit, model_id,
                            modelname, warn_time, temp_predeter, ip_port='23.49.171.62:8821')
        try:
            cursor.execute(insertdeterpre_sql,(unit,model_id,temp_time,temp_predeter,pre_threshold,version))
            print('存储一个预测点！', str(unit) + str(model_id))
        except:
            print("unable to insert into deterpre table !")
    # if flag == 0:
    #     warnsig = 0
    #     warn_runtime = temp_time - pre_steps
    #     warn_time = get_warntime(host, user, password, port, unit, model_id, warn_runtime,version)
    #     try:
    #         cursor.execute(insertwarn_sql, (unit, model_id, type, warn_time, modelname, warnsig,equip))
    #         print('存入一个未预警记录到tre_warn表中')
    #     except:
    #         print("unable to insert into tre_warn table !")
    conn.commit()
    conn.close()

# 保存劣化预测结果
# def deterpre_starage(host, user, password, port, unit, model_id, prestart_runtime, predeter,pre_steps,version):
#     type = 1
#     version = int(version)
#     prestart_runtime = int(prestart_runtime)
#     if not isinstance(predeter,list):
#         predeter = predeter.tolist()
#     [pre_threshold,modelname] = read_thresholdname(host, user, password, port, unit,model_id)
#     equip = read_equipment(host,user,password,port,unit,model_id)
#     conn = pymysql.connect(host, user, password, port)
#     cursor = conn.cursor()
#     insertdeterpre_sql = "INSERT INTO tre_deterpre(unit,id,pretime,predeter,threshold,version) VALUES(%s,%s,%s,%s,%s,%s)"
#     insertwarn_sql = "insert into tre_warn(unit,id,type,time,name,warn,equip)values(%s,%s,%s,%s,%s,%s,%s)"
#     flag = 0
#     for i in range(len(predeter)):
#         temp_predeter = predeter[i]
#         temp_predeter = float(temp_predeter)
#         warnsig = 0
#         temp_time = prestart_runtime + i
#         if temp_predeter > pre_threshold:
#             flag = 1
#             warnsig = 1
#             warn_runtime = temp_time - pre_steps
#             warn_time = get_warntime(host,user,password,port,unit,model_id,warn_runtime,version)
#             try:
#                 cursor.execute(insertwarn_sql,(unit,model_id,type,warn_time,modelname,warnsig,equip))
#                 print("存入一个预警记录到tre_warn表")
#             except:
#                 print("unable to insert into tre_warn table !")
#             postforewarnhdy(host, user, password, port, unit, model_id,
#                             modelname, warn_time, pre_threshold, temp_predeter, ip_port='23.49.171.53:8085')
#             postforewarnnr(host, user, password, port, unit, model_id,
#                             modelname, warn_time, temp_predeter, ip_port='23.49.171.62:8821')
#         try:
#             cursor.execute(insertdeterpre_sql,(unit,model_id,temp_time,temp_predeter,pre_threshold,version))
#             print('存储一个预测点！', str(unit) + str(model_id))
#         except:
#             print("unable to insert into deterpre table !")
#     if flag == 0:
#         warnsig = 0
#         warn_runtime = temp_time - pre_steps
#         warn_time = get_warntime(host, user, password, port, unit, model_id, warn_runtime,version)
#         try:
#             cursor.execute(insertwarn_sql, (unit, model_id, type, warn_time, modelname, warnsig,equip))
#             print('存入一个未预警记录到tre_warn表中')
#         except:
#             print("unable to insert into tre_warn table !")
#     conn.commit()
#     conn.close()


# 发送预警信息hdy
def postforewarnhdy(host, user, password, port, unit, id, name, warntimestamp, threshold, prevalue, ip_port):
    tablename = 'tre_deter_threshold'
    unit = str(unit)
    id = str(id)
    warntime = timestamptodate(warntimestamp)
    threshold = str(threshold)
    prevalue =str(prevalue)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT equipment FROM " + tablename + " WHERE unit = " + unit + " and id = " + id
    equipment = "水泵水轮机"
    try:
        cursor.execute(selectsql)
        result = cursor.fetchall()
        equipment = result[0][0]
    except:
        print('unable to get equipment !')
    finally:
        conn.close()
    url = 'http://' + ip_port + '/ecidi-cmp/jkpjWarn/jkpjWarn/add'
    data = [{"name": name,
             "equipName": unit + "号" + equipment,
             "startTime": warntime,
             "warnNum": threshold,
             "realNum": prevalue}]
    try:
        res = requests.post(url=url, json=data)
        print(res.text)
    except:
        print('unable to post forewarning !')

# 发送预警信息nr
def postforewarnnr(host, user, password, port, unit, id, name, warntimestamp, prevalue, ip_port):
    tablename = 'tre_deter_threshold'
    unit = str(unit)
    id = str(id)
    prevalue = str(prevalue)
    warntime = timestamptodate(warntimestamp)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT equipment FROM " + tablename + " WHERE unit = " + unit + " and id = " + id
    equipment = "水泵水轮机"
    try:
        cursor.execute(selectsql)
        result = cursor.fetchall()
        equipment = result[0][0]
    except:
        print('unable to get equipment !')
    finally:
        conn.close()
    url = 'http://' + ip_port + '/nariData/jkpjAlarm/add'
    data = [{"name": name,
             "equipName": unit + "号" + equipment,
             "startTime": warntime,
             "childEquip": "",
             "warningLevel": "趋势预警",
             "description": name
             }]
    try:
        res = requests.post(url=url, json=data)
        print(res.text)
    except:
        print('unable to post forewarnnr !')


# 发送报警信息
def postalarm(host, user, password, port, unit, id, name,timestamp,ip_port):
    tablename = 'tre_ana_threshold'
    unit = str(unit)
    id = str(id)
    namelist = []
    alarmtime = timestamptodate(timestamp)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT equipment,quanxi,detailequ FROM " + tablename + " WHERE unit = " + unit + " and id = " + id
    try:
        cursor.execute(selectsql)
        result = cursor.fetchall()
        namelist = result[0]
    except:
        print('unable to get equipment !')
    conn.close()
    if len(namelist) == 0:
        print('unable to read equipment !')
        return -1
    childEquip = namelist[2]
    if namelist[1] ==None:
        equipment = unit + "号" + namelist[0]
    else:
        equipment=namelist[1]
    url = 'http://' + ip_port + '/ecidi-cmp//jkpjAlarm/jkpjAlarm/add'
    data = [{"name": name,
            "equipName": equipment,
            "startTime": alarmtime,
             "childEquip": childEquip,
             "warningLevel":"报警",
             "description":name}]
    try:
        res = requests.post(url=url, json=data)
        print(res.text)
    except:
        print('unable to post alarm !')

# def deterpre_starage(host, user, password, port, predeter_result, pre_startruntime, unit, model_id, model_version, pre_steps):
#     type = 1
#     pre_startruntime = int(pre_startruntime)
#     id_version = str(model_id) + str(model_version)
#     if not isinstance(predeter_result,list):
#         predeter_result = predeter_result.tolist()
#     [pre_threshold,modelname] = read_thresholdname(host, user, password, port, model_id,model_version)
#     conn = pymysql.connect(host, user, password, port)
#     cursor = conn.cursor()
#     insertdeterpre_sql = "INSERT INTO tre_deterpre(pretime,predeter,warnsig,id_version) VALUES(%s,%s,%s,%s)"
#     insertwarn_sql = "insert into tre_warn(unit,id,type,time,name,warn)values(%s,%s,%s,%s,%s,%s)"
#     for i in range(len(predeter_result)):
#         warnsig = 0
#         tem_time = pre_startruntime + i + 1
#         if predeter_result[i] > pre_threshold:
#             warnsig = 1
#             warn_runtime = tem_time - pre_steps
#             warn_time = get_warntime(host,user,password,port,warn_runtime,id_version)
#             cursor.execute(insertwarn_sql,(unit,model_id,type,warn_time,modelname,warnsig))
#         cursor.execute(insertdeterpre_sql,(tem_time,predeter_result[i],warnsig,id_version))
#         conn.commit()
#     conn.close()

# 读取预警发生的时间
def get_warntime(host,user,password,port,unit,model_id,runtime,version):
    runtime = str(runtime)
    unit = str(unit)
    model_id = str(model_id)
    version = str(version)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    select_sql ="select time from tre_deterdata where unit = " + unit+ " and id = " +model_id+\
                " and runtime =" +runtime + " and version= "+version
    try:
        cursor.execute(select_sql)
        result = cursor.fetchall()
    except:
        print("unable to get warn time !")
        result = []
    conn.close()
    warntime = result[0][0]
    return warntime

# def get_warntime(host,user,password,port,unit,model_id,runtime):
#     runtime = str(runtime)
#     unit = str(unit)
#     model_id = str(model_id)
#     conn = pymysql.connect(host, user, password, port)
#     cursor = conn.cursor()
#     select_sql ="select time from tre_deterdata where unit = " + unit+ " and id = " +model_id+ " and runtime =" +runtime
#     try:
#         cursor.execute(select_sql)
#         result = cursor.fetchall()
#     except:
#         print("unable to get warn time !")
#         result = []
#     conn.close()
#     warntime = result[0][0]
#     return warntime

# 读取不同劣化模型阈值和模型名称
def read_thresholdname(host, user, password, port,unit,model_id):
    unit = str(unit)
    model_id = str(model_id)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT val,name FROM tre_deter_threshold WHERE unit= "\
          + unit +" and id =" + model_id
    try:
        cursor.execute(selectsql)
        result = cursor.fetchall()
    except:
        print('unable to read deter_threshold table !')
        result = []
    conn.close()
    deter_threshold = result[0][0]
    modelname = result[0][1]
    return deter_threshold,modelname

# 读取不同劣化模型的设备名称equip
def read_equipment(host, user, password, port,unit,model_id):
    unit = str(unit)
    model_id = str(model_id)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT equipment FROM tre_deter_threshold WHERE unit= "\
          + unit +" and id =" + model_id
    try:
        cursor.execute(selectsql)
        result = cursor.fetchall()
    except:
        print('unable to read deter_threshold table !')
        result = []
    conn.close()
    equipment = result[0][0]
    return equipment

# 返回当前和上一天的日期
def get_nowlastday():
    now = datetime.datetime.now()
    now_year = now.year
    now_month = now.month
    now_day = now.day
    last = now - datetime.timedelta(days=1)
    last_year = last.year
    last_month = last.month
    last_day = last.day
    return now_year,now_month,now_day,last_year,last_month,last_day


# 返回前一天的状态数据
def read_real_bool_data(host, user, password, port, table_id):
    [now_year, now_month, now_day, last_year, last_month, last_day] = get_nowlastday()
    tss1 = str(last_year) + '-' + str(last_month) + '-' + str(last_day) + ' 00:00:00'
    tss2 = str(now_year) + '-' + str(now_month) + '-' + str(now_day) + ' 00:00:00'
    timearray1 = time.strptime(tss1, '%Y-%m-%d %H:%M:%S')
    timearray2 = time.strptime(tss2, '%Y-%m-%d %H:%M:%S')
    timestamp1 = int(time.mktime(timearray1))
    timestamp2 = int(time.mktime(timearray2))
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    if last_month < 10:
        last_month = str(0) + str(last_month)
    else:
        last_month = str(last_month)
    table_name = 'bool' + '_' + str(table_id) + '_' + str(last_year) + '_' + last_month
    sql = "SELECT * FROM " + str(table_name) + " WHERE t >=" + str(timestamp1) +" and t <= " + str(timestamp2)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print('fetch data!')
    except:
        print('Uable to fetch data!')
    conn.close()
    return results

# 返回前一天的浮点数据
def read_real_float_data(host, user, password, port,table_id):
    [now_year, now_month, now_day, last_year, last_month, last_day] = get_nowlastday()
    tss1 = str(last_year) + '-' + str(last_month) + '-' + str(last_day) + ' 00:00:00'
    tss2 = str(now_year) + '-' + str(now_month) + '-' + str(now_day) + ' 00:00:00'
    timearray1 = time.strptime(tss1, '%Y-%m-%d %H:%M:%S')
    timearray2 = time.strptime(tss2, '%Y-%m-%d %H:%M:%S')
    timestamp1 = int(time.mktime(timearray1))
    timestamp2 = int(time.mktime(timearray2))
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    if last_month < 10:
        last_month = str(0) + str(last_month)
    else:
        last_month = str(last_month)
    table_name = 'float' + '_' + str(table_id) + '_' + str(last_year) + '_' + last_month
    sql = "SELECT * FROM " + str(table_name) + " WHERE t >=" + str(timestamp1) +" and t <= " + str(timestamp2)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print('fetch data!')
    except:
        print('Uable to fetch data!')
    conn.close()
    return results

# 读取抽水发电态下过去一天的数据
def get_steady_deter_realdata1(starttime, endtime, url, pumpstate_id, powerstate_id, data_idlist):
    data_pump=[]; data_power=[]; result_pump=[]; result_power=[]; result_pumptime=[]; result_powertime=[]
    pump_bool_result = basic_query(pumpstate_id, datatype=1, starttime=starttime, endtime=endtime, interval=-1, url=url)
    power_bool_result = basic_query(powerstate_id, datatype=1, starttime=starttime, endtime=endtime, interval=-1, url=url)
    for index in range(len(data_idlist)):
        data_pump.append([])
        data_power.append([])
    for i in range(len(data_idlist)):
        tempdata_pump = [];tempdata_power = []; temp_pump = []; temp_power = []
        float_result = basic_query(data_idlist[i], datatype=0, starttime=starttime, endtime=endtime, interval=0)
        tempdata_pump = steady_deter_datalist(float_result,pump_bool_result)
        tempdata_power = steady_deter_datalist(float_result,power_bool_result)
        data_pump[i] = data_pump[i] + tempdata_pump
        data_power[i] = data_power[i] + tempdata_power
        temp_pump = get_listrow(1,data_pump[i])
        temp_power = get_listrow(1,data_power[i])
        result_pumptime = get_listrow(0, data_pump[i])
        result_powertime = get_listrow(0, data_power[i])
        result_pump.append(temp_pump)
        result_power.append(temp_power)
    return result_pump, result_power, result_pumptime,result_powertime

# 读取指定时间段下通道的值,并按时间顺序输出
def read_settime_data(host, user, password, port,table_id,timestamp1,timestamp2):
    time1 = datetime.datetime.fromtimestamp(timestamp1)
    table_year = time1.year
    table_month = time1.month
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    if table_month < 10:
        table_month = str(0) + str(table_month)
    else:
        table_month = str(table_month)
    if port == "XJdatabase_core" or port == "XJ_core":
        table_name = 'float' + '_' + str(table_id) + '_' + str(table_year) + '_' + table_month
    else:
        table_name = 'bool' + '_' + str(table_id) + '_' + str(table_year) + '_' + table_month
    sql = "SELECT t,v FROM " + str(table_name) + " WHERE t>=" + str(timestamp1) + " and t <=" + str(
        timestamp2) + " order by t"
    results = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print('Uable to fetch data!')
    conn.close()
    return results

def get_steady_deter_realdata(host, user, password, bool_port, float_port, pump_state,power_state, datalist):
    data_pump = []; data_power = []; result_pump = []; result_power = []
    pump_bool_result = read_real_bool_data(host, user, password, bool_port, pump_state)
    power_bool_result = read_real_bool_data(host, user, password, bool_port, power_state)
    for _ in range(len(datalist)):
        data_pump.append([])
        data_power.append([])
    for i in range(len(datalist)):
        tempdata_pump = [];tempdata_power = []; temp_pump = []; temp_power = []
        float_result = read_real_float_data(host, user, password, float_port, datalist[i])
        tempdata_pump = steady_deter_datalist(float_result,pump_bool_result)
        tempdata_power = steady_deter_datalist(float_result,power_bool_result)
        data_pump[i] = data_pump[i] + tempdata_pump
        data_power[i] = data_power[i] + tempdata_power
        temp_pump = get_listrow(1,data_pump[i])
        temp_power = get_listrow(1,data_power[i])
        result_pump.append(temp_pump)
        result_power.append(temp_power)
    return result_pump, result_power

# 读取劣化表格最新运行次
def read_deterruntime(host, user, password, port,unit,model_id,version):
    unit = str(unit)
    model_id = str(model_id)
    version =str(version)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT runtime FROM tre_deterdata where unit = "+unit+" and id ="+ model_id + " and version =" \
            + version + " order by runtime desc"
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchall()
    except:
        print('Uable to fetch data')
    conn.close()
    result = result1[0][0]
    return result

# 读取劣化序列
def read_deterlist(host, user, password, port,unit,model_id,version,length):
    unit = str(unit)
    model_id = str(model_id)
    version =str(version)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT deter FROM tre_deterdata where unit = "+unit+" and id ="+ model_id + " and version =" \
            + version + " order by runtime desc"
    result = []
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchmany(length)
    except:
        print('Uable to fetch data')
    conn.close()
    result1 = result1[::-1]
    for i in range(len(result1)):
        result.append(result1[i][0])
    return result

# 读取劣化表格劣化度对应时间
def read_detertime(host, user, password, port,unit,model_id,version,length):
    unit = str(unit)
    model_id = str(model_id)
    version =str(version)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT time FROM tre_deterdata where unit = "+unit+" and id ="+ model_id + " and version =" \
            + version + " order by runtime desc"
    result = []
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchmany(length)
    except:
        print('Uable to fetch data')
    conn.close()
    result1 = result1[::-1]
    for i in range(len(result1)):
        result.append(result1[i][0])
    return result

# 读取劣化表格记录
# def read_deterlist(host, user, password, port,id,update_times,length):
#     id_version = str(id) + str(update_times)
#     conn = pymysql.connect(host, user, password, port)
#     cursor = conn.cursor()
#     sql = "SELECT * FROM tre_deterdata where id_version = "+id_version+" order by time desc"
#     result = []
#     try:
#         cursor.execute(sql)
#         results1 = cursor.fetchmany(length)
#         results2 = results1[::-1]
#         result = np.array(results2)
#     except:
#         print('Uable to fetch data')
#     conn.close()
#     return result

# 读取预测表最新运行次数
def read_preruntime(host, user, password, port,unit,model_id,version):
    unit = str(unit)
    model_id = str(model_id)
    version = str(version)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    result = []
    selectsql = "SELECT pretime FROM tre_deterpre where unit = " + unit + " and id =" + model_id + " and version =" \
                + version + " order by pretime desc"
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchall()
    except:
        print("Uable to fetch data")
    conn.close()
    result = result1[0][0]
    return result

# 读取劣化预测结果表格记录
# def read_pre_deterlist(host, user, password, port,id,update_times,length):
#     id_version = str(id)+str(update_times)
#     conn = pymysql.connect(host, user, password, port)
#     cursor = conn.cursor()
#     result = []
#     sql = "SELECT * FROM tre_deterpre where id_version = " + id_version + " order by pretime desc"
#     try:
#         cursor.execute(sql)
#         results1 = cursor.fetchmany(length)
#         results2 = results1[::-1]
#         result = np.array(results2)
#     except:
#         print("Uable to fetch data")
#     conn.close()
#     return result

# 建立劣化模型所用参数表
def build_parametertable(host, user, password, port):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    creatsql = "CREATE TABLE if not exists tre_deter_para(unit int not null,version int not null," \
               "savepath varchar(100) not null," \
               "primary key(unit,version)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    try:
        cursor.execute(creatsql)
    except:
        print('unable to build parameter table !')
    conn.close()

# 读取劣化模型最新的版本号、保存路径
def read_deterpath(host, user, password, port, unit):
    unit = str(unit)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    result = []
    selectsql = "SELECT savepath FROM tre_deter_para where unit = " + unit
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchall()
    except:
        print("Unable to read deterpara table!")
    conn.close()
    result = result1[0][0]
    return result

# 存储劣化模型最新的版本号、保存路径
def write_parametertable(host, user, password, port,unit,savepath):
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    savepath = str(savepath)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    insertsql = "INSERT INTO tre_deter_para(unit,savepath) VALUES(%s,%s)"
    try:
        cursor.execute(insertsql, (unit,savepath))
        conn.commit()
        print('successfully insert into deter_para table !')
    except:
        print('unable to insert into deter_para table !')
    conn.close()

# 读取模型更新时间加flag,返回更新时间加上3个月，为更新结束时间
def read_updatetime_flag(host, user, password, port, unit):
    unit = str(unit)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT time,flag FROM tre_deter_update where unit = "+unit+ " order by time desc"
    result1 = []
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchall()
    except:
        print('Uable to fetch data')
    conn.close()
    if len(result1) == 0:
        return []
    else:
        starttime = result1[0][0]
        endtime = starttime + 86400*90
        flag = result1[0][1]
        return [starttime,endtime,flag]

# 读取模型最新劣化预测模型的版本号，即flag为1的最新时间
def read_determodel_version(host, user, password, port, unit):
    unit = str(unit)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    selectsql = "SELECT time FROM tre_deter_update where unit = "+unit+" and flag = 1 "+ " order by time desc"
    starttime = 0
    result1 =[]
    try:
        cursor.execute(selectsql)
        result1 = cursor.fetchall()
    except:
        print('Uable to fetch data')
    conn.close()
    if len(result1) == 0:
        return starttime
    else:
        starttime = result1[0][0]
        return starttime

# 更新劣化模型更新标志，
def update_updatetime_flag(host, user, password, port, unit,flag):
    unit = str(unit)
    flag = str(flag)
    conn = pymysql.connect(host, user, password, port)
    cursor = conn.cursor()
    update_sql = "update tre_deter_update set flag ="+ flag + " where unit= " + unit
    try:
        cursor.execute(update_sql)
        conn.commit()
    except:
        print('Uable to update deterupdateflag')
    conn.close()

# 发送趋势预警历史趋势
def posttrend(host, user, password, port, unit, id,start_runtime,hisdeter_data, ip_port):
    unit = str(unit)
    id = str(id)
    start_runtime = int(start_runtime)
    if not isinstance(hisdeter_data,list):
        hisdeter_data = hisdeter_data.tolist()
    [pre_threshold, modelname] = read_thresholdname(host, user, password, port, unit, id)
    url = 'http://'+ ip_port + '/ecidi-cmp/jkpjTrendData/jkpjTrendData/add'
    data = []
    modelname = str(modelname)
    unitname1 = modelname[-6:-2]
    unitname = unit+"号机"+ unitname1
    for i in range(len(hisdeter_data)):
        runtime = start_runtime + i
        runtime = str(runtime)
        deter = hisdeter_data[i]
        deter = str(deter)
        dict1 = {"name": modelname,
             "trendValue": deter,
             "num": runtime,
            "unit": unitname}
        data.append(dict1)
    try:
        res = requests.post(url=url, json=data)
        print(res.text)
    except:
        print('unable to post trend !')

# 计算劣化度，判断模型是否更新
def judgeupdate(host,user,password,result_port,unit,savepath,starttimestamp,endtimestamp,
                unit_state,inputdata_idlist,outputdata_idlist,
                sampleInterval,delaytime,advancetime,url1,url2,input_index,input_perunit,output_perunit):
    updateflag = 0
    version = read_determodel_version(host,user,password,result_port,unit)
    if version == 0:
        print(str(unit) + "号机组读取模型版本号错误！")
        return updateflag
    # 导入各机组历史健康状态数据
    readstart = time.clock()
    inputdatalist = getdata_url(starttimestamp, endtimestamp,unit_state,inputdata_idlist,sampleInterval,
                                delaytime,advancetime,url1,url2)
    outputdatalist =getdata_url(starttimestamp, endtimestamp,unit_state,outputdata_idlist,sampleInterval,
                                delaytime,advancetime,url1,url2)
    readend = time.clock()
    print('readtime:', readend - readstart)
    if len(inputdatalist[0]) == 0:
        updateflag = 0
        return updateflag
    # 保证查询的数据长度一致
    inputdatalist = check_hisdata(inputdatalist, starttimestamp, endtimestamp, unit_state,
                                  inputdata_idlist, sampleInterval, delaytime, advancetime, url1, url2)
    outputdatalist =check_hisdata(outputdatalist, starttimestamp, endtimestamp, unit_state,
                                  outputdata_idlist, sampleInterval, delaytime, advancetime, url1, url2)
    # 数据转换，第一行为时间，每一行为通道数据
    deter_in, deter_out = deal3Ddata(inputdatalist, outputdatalist)
    # 输入项加入开机时间
    deter_runtime = already_runtime(deter_in[0], delaytime, sampleInterval)
    deter_in.append(deter_runtime)
    # 删除功率低于370的点
    [deter_in, deter_out] = delete_littlepowerdata(deter_in, deter_out)
    deter_in_notime = deter_in[1:]
    # 为每一个通道建立劣化序列并预测,先选择输入输出,第一行为时间。最后再分别构造摆度和振动的融合序列并预测
    deterlist_all = []
    j = 0
    for k in range(len(deter_out) - 1):
        model_input_index = input_index[j][k]
        model_input_withtime = []
        model_output_withtime = []
        model_input_perunit = []
        model_output_perunit = []
        model_input_withtime.append(deter_in[0])
        model_output_withtime.append(deter_out[0])
        for m in (model_input_index):
            model_input_withtime.append(deter_in_notime[m])
            model_input_perunit.append(input_perunit[m])
        model_output_withtime.append(deter_out[k + 1])
        model_output_perunit.append(output_perunit[k])
        # 删除z向振动的峰值点，均值+3*标准差
        if k == 8 or k == 11 or k == 14:
            model_input_withtime, model_output_withtime = delete_outlier(model_input_withtime,
                                                                         model_output_withtime, row_num=1)
        # 按标幺值归一化
        per_modelin = per_unit(model_input_withtime, model_input_perunit)
        per_modelout = per_unit(model_output_withtime, model_output_perunit)
        per_modelin = np.array(per_modelin)
        per_modelout = np.array(per_modelout)
        per_modelout = np.reshape(per_modelout, (per_modelout.shape[1],))
        # 转置
        per_modelin = per_modelin.T
        modelnum = k + 1 + (len(deter_out) - 1) * j
        # 构造劣化序列,先计算健康值
        healthymodel = load_model(savepath + '/healthymodel' + str(unit) + str(modelnum) + '_' + str(version) + '.h5')
        predict_data = healthymodel.predict(per_modelin)
        predict_data = np.array(predict_data)
        predict_data = np.reshape(predict_data, (predict_data.shape[0],))
        # 反归一化
        Deteroutput = per_modelout * output_perunit[k]
        Predict_data = predict_data * output_perunit[k]
        # 存储健康值和实际值
        timelist1 = model_input_withtime[0]
        # 计算劣化度
        deter_data = (Deteroutput - Predict_data) / (output_perunit[k] - Predict_data)
        # 劣化度按次取平均
        deter_runtime = model_input_withtime[-1]
        [deterlist_bytime, deter_firsttime] = deterlist_byruntime(timelist1, deter_runtime, deter_data, delaytime)
        deterlist_mean = []
        for d in range(len(deterlist_bytime)):
            tempdeter = np.array(deterlist_bytime[d]).mean()
            deterlist_mean.append(tempdeter)
        deterlist_all.append(deterlist_mean)
    # 构建融合摆度劣化序列和振动劣化序列,摆度0-5，振动6-14,需要读取第一个摆度、振动的劣化时间，不要z向振动
    deterlist_all = np.array(deterlist_all)
    bd_deterlist = (np.array(deterlist_all[0]) + np.array(deterlist_all[1]) + np.array(deterlist_all[2]) +
                    np.array(deterlist_all[3]) + np.array(deterlist_all[4]) + np.array(deterlist_all[5])) / 6
    zd_deterlist = (np.array(deterlist_all[6]) + np.array(deterlist_all[7]) + np.array(deterlist_all[9]) +
                    np.array(deterlist_all[10]) + np.array(deterlist_all[12]) + np.array(deterlist_all[13])) / 6
    bd_num = 0
    zd_num = 0
    for i in range(len(bd_deterlist)):
        if bd_deterlist[i] < 0.1:
            bd_num = bd_num +1
    for j in range(len(zd_deterlist)):
        if zd_deterlist[j] < 0.1:
            zd_num = zd_num +1
    if bd_num / len(bd_deterlist) > 0.9 and zd_num / len(zd_deterlist) > 0.9:
        updateflag = 1
    return updateflag

# 增加写入日志功能
def write_to_work_log(host, user, password, database, timestamp, unit, model_name, log_type, log_info):
    """
    time: timestamp
    unit: 1,2,3,4
    model_name: "tre_deter", "tre_ana"
    log_type: "infor", "warning", "error", "notest"
    log_infor: "模型开始工作", "模型结束工作", "模型运行打卡"
    """
    table_name = "model_work_log"
    conn = pymysql.connect(host, user, password, database)
    cursor = conn.cursor()
    execspl = "insert into " + table_name + " (time, unit, model_name, log_type, log_info)  value(%s,%s,%s,%s,%s)"
    try:
        cursor.execute(execspl, (timestamp, unit, model_name, log_type, log_info))
        conn.commit()
    except Exception as e:
        print(e)
        print('Uable to write into model_work_log')
    finally:
        conn.close()
