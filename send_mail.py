
# coding: utf-8

# In[ ]:


# --------这些模块及函数的作用是处理email----------------
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase   
from email.utils import parseaddr, formataddr
import smtplib
# --------------------------------------------------

# --------这些模块及函数的作用是时间及定时器--------------
import os
import datetime
from threading import Timer 
# --------------------------------------------------


# --------处理日志，使用内置模块logging------------------------------------------
import logging      # 日志模块
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# 注意函数basicConfig是一个一次性的简单配置工具，也就是说只有在第一次调用该函数时会起作用
logging.basicConfig(filename='my.log',level=logging.INFO,format=LOG_FORMAT)
#-----------------------------------------------------------------------------


# --------处理编码，使用内置模块chardet----------------
import chardet
# 得到文件的编码
def get_codetype(file):
    with open(file,'rb') as f:
        data=f.read()
        return chardet.detect(data)['encoding']
# --------------------------------------------------

# ---------规范化电子邮件地址-----------------------------------
def _format_addr(s):
    # parseaddr解析字符串中的email地址
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
# -----------------------------------------------------------


# ---------------------------------定义一些全局变量-----------------------------------------------------
# 构建一个字典，发送的邮件名称，密码，注意这里的密码其实是你开通邮件smtp服务时的验证码和smtp服务器名称，以及目的邮件地址
mail_dict=({'from_addr':'545139870@qq.com','password':'zvvsilbhxelzbaja',
           'smtp_server':'smtp.qq.com','to_addr':['563425959@qq.com','jiangql@jiahuan.com','137897658@qq.com']})
from_addr = mail_dict['from_addr']  # 字符串，发件人的地址
password = mail_dict['password']
to_addr = mail_dict['to_addr']      # 注意收件人地址是一个列表，里面是一个或者多个收件人的地址
smtp_server = mail_dict['smtp_server']
# ----------------------------------------------------------------------------------------------------


# ---------------------------从toSave.csv文件中得到群组关系------------------
# 从’tosave.csv'配置文件中得到有几个组，那么每天就会生成几个文件，也就是要传回的文件
def get_group(config_file):
    # step1:先判断配置文件是否存在
    if os.path.exists(config_file):    
        # 得到‘toSave.csv’的编码
        encoding=get_codetype(config_file)
        i=0
        group_list=[]
        with open(config_file,encoding=encoding) as f:
            for line in f:
                # 前两条记录不是有效记录
                if i>=2:
                    line.encode('UTF-8')
                    group_list.append(line.split(',')[1])
                i+=1 
    
        # 通过set没有重复元素的特点，去除重复元素,并且重新转化成list
        group_list=list(set(group_list))
        return group_list
    else:
        # 配置文件不存在，把这个信息写入到日志文件中，并且返回False
        logging.error("config file is not exists!")
        return False
# ------------------------------------------------------------------------   
    
# ---------------得到当前时间以及得到需要发送的附件名称-------------------------
def get_datetime():     
    # 初始化发送标记位 False的时候不发送，True的时候发送
    send_flag=False
        
    # 得到前一天的日期，因为当前发送的是前一天的数据文件
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)   #1天前
    yesterday = (today - oneday).strftime('%Y_%m_%d')
    year,month,day=yesterday.split('_')
    main_dir='Hist_'+year
    sub_dir='Hist_'+year+'_'+month
    total_dir=main_dir+'/'+sub_dir
    
    # 首先建一个空列表，放多个附件文件完整目录
    filename=[]
    
    group=get_group('toSave.csv')
    if group: 
        for sub_group in group:
            # 把每个附件文件的完整目录添加到filename列表中
            filename.append(total_dir+'/'+sub_group+'_'+year+'_'+month+'_'+day+'.csv')
        # ---------------------------------------------------------------------------
    
        # 返回当前时间，用当前的时间来判断每天的触发发送标注位，每天发两次，早上8点一次，晚上8点一次
        # --------------------------------------------------------------------------
        timelist=datetime.datetime.now().strftime('%X')
        hour,minute,second=timelist.split(':')

        if int(minute)%2==0:
        #if hour=='08' or hour=='20':
            send_flag=True
        else:
            send_flag=False
        # -----------------------------------------------------------------------------
    else:
        pass
    # 返回值为要发送的附件文件的列表和执行标签
    return filename,send_flag
# -----------------------------------------------------------------------------------------
        


# ------------------------------发送邮件----------------------------------------------------
def send_mail_to_jiahua(filename_list): 
    """
    参数：filename 字符串列表 需要发送附件的文件的带目录的文件名 
         例如 ['/Users/eric/a.csv','/Users/eric/b.csv']
    """
    
    if not filename_list:
        print('filename_list is empty!')
        return
    # 发送过程错误码，True有错，False没有错产生
    error_code=False
    # 邮件对象:
    msg = MIMEMultipart()
    msg['From'] = _format_addr('langxi dainchang <%s>' % from_addr)
    #msg['To'] = _format_addr('administrator <%s>' % to_addr[0])
    msg['To']=','.join(to_addr)
    msg['Subject'] = Header('device data……', 'utf-8').encode()

    # 邮件正文是MIMEText:
    msg.attach(MIMEText('This is a data file...', 'plain', 'utf-8'))

    # 添加附件就是加上一个MIMEBase，从本地读取一个csv文件,循环一次读取一个，数量取决于len(filename_list)
    for file in filename_list:
        # 先判断文件是否存在
        if os.path.exists(file):
            with open(file, 'rb') as f:
                # 设置附件的MIME和文件名，这里是csv类型:
                mime = MIMEBase('data', 'csv', filename=file.split('/')[-1])
                # 加上必要的头信息:
                mime.add_header('Content-Disposition', 'attachment', filename=file.split('/')[-1])
                mime.add_header('Content-ID', '<0>')
                mime.add_header('X-Attachment-Id', '0')
                # 把附件的内容读进来:
                mime.set_payload(f.read())
                # 用Base64编码:
                encoders.encode_base64(mime)
                # 添加到MIMEMultipart:
                msg.attach(mime)
        else:
            logging.error("data file is not exists!")
            print(file +'is not exists！')
    
    # 把日志文件通过附件发回，不管数据的文件不存在还是不存在
    with open('my.log', 'rb') as f:
        mime = MIMEBase('loggin', 'log', filename='my.log')
        # 加上必要的头信息:
        mime.add_header('Content-Disposition', 'attachment', filename='my.log')
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(f.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
        # 添加到MIMEMultipart:
        msg.attach(mime)    
    
    try:        
        server = smtplib.SMTP_SSL("smtp.qq.com",465)
        #server.set_debuglevel(1)  #打印出和SMTP服务器交互的所有信息
        server.login(from_addr, password)      
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
    except:
        logging.error("smtp error,send fail!")
        error_code=True
    finally:
        if error_code:
            print('send fail')
        else:
            logging.info('send success!')
            print('send success')

            
            
# ---------------------定义定时器函数，每隔1小时需要做的动作---------------------------------------
timer_count=3600
def fun_timer():  
    print('aaa')
    filename_list,send_flag=get_datetime()
    print(filename_list)
    print(send_flag)
    if send_flag:
        print('send_mail')
        #send_mail_to_jiahua(filename_list=filename_list)
    
    global timer                  # 直接全局timer这个定时器就够了，复用一下
    timer = Timer(timer_count,fun_timer) # 1小时调用一次函数,定时器构造函数主要有2个参数，第一个参数为时间，
                                  # 第二个参数为函数名    
    timer.start()                 # 启动定时器
# -----------------------------------------------------------------------------------------
    
    
# Timer（定时器）是Thread的派生类，用于在指定时间后调用一个方法，和其他比如c的定时器是不同的，c里是会自动循环的，这里的Timer则是不会    
timer = Timer(1,fun_timer)       # 定义初次定时器,1s后执行fun_timer
timer.start()                    # 启动定时器


# In[23]:


if __name__ == "__main__":   
    timer = Timer(1,fun_timer)  #首次启动
    timer.start()

