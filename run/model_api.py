from flask import Flask, request, jsonify,render_template
import joblib
import pandas as pd
import io
import json
import pandas as pd
import numpy as np

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

def send_alert_email():
    # 配置邮箱信息
    smtp_server = 'smtp.qq.com'
    smtp_port = 465  # SSL 端口
    smtp_user = '3592569640@qq.com'
    smtp_password = 'izkeehprhhxzdbeb'  # QQ邮箱生成的授权码
    receiver = '3592569640@qq.com'

    # 创建邮件内容
    message = MIMEText('老大 你的电脑正在被nmap扫描', 'plain', 'utf-8')

    message['From'] = formataddr(('Python测试', receiver))
    message['To'] = formataddr(('收件人姓名', receiver))
    message['Subject'] = '入侵检测报警'

    try:
        # 使用 SSL 加密连接
        smtp_obj = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp_obj.login(smtp_user, smtp_password)
        smtp_obj.sendmail(smtp_user, [receiver], message.as_string())
        smtp_obj.quit()
        print("报警邮件发送成功！")
    except Exception as e:
        print("邮件发送失败:", e)


log_list = []  # 保存历史预测日志
app = Flask(__name__)

# 加载模型
model_filename = '../train/random_forest_model.pkl'
grid_model = joblib.load(model_filename)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 获取原始请求数据并解码
        raw_data = request.data.decode('utf-8')  # bytes -> str
        print("Received raw data:", raw_data)

        # 将字符串解析为字典
        json_data = json.loads(raw_data)  # str -> dict

        # 提取 csv 字符串，并替换掉转义字符
        csv_str = json_data["csv_str"].replace("\\n", "\n").strip()
        print("CSV string:", csv_str)

        # 用 StringIO 转为文件对象供 pandas 读取
        data_io = io.StringIO(csv_str)
        df = pd.read_csv(data_io, header=None)  # 如果没有表头，就设 header=None
        
        print("set column")
        # 如果模型要求特定的列名，可以在这里设置列名
        df.columns = [' ','ts', 'uid', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p', 'proto', 'service', 'duration', 
              'orig_bytes', 'resp_bytes', 'conn_state', 'local_orig', 'local_resp', 'missed_bytes', 'history', 
              'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes', 'tunnel_parents']


        # 添加行号列，行号从 1 开始
        df.iloc[:, 0] = range(0, len(df))  

        # # 如果有缺失值，需要先填充或删除缺失值
        df.replace('-', np.nan, inplace=True)
    
        #设置resp_bytes 但后面不需要
        df[["resp_ip_bytes", "resp_bytes"]][df["resp_ip_bytes"]==0]
        for i in df[df["resp_ip_bytes"]==0].index:
            df.loc[i, "resp_bytes"] = 0
        
        #设置service
        df["service"] = df["service"].replace({"ntp":0, "dns":1, "gssapi":2, "dns":3,"http":4,"krb_tcp":5})
        df["service"] = df["service"].fillna(6)
    
        #设置proto
        df["proto"] = df["proto"].replace({"tcp":0, "udp":1, "icmp":2})
        #设置history
        df["history"] = df["history"].replace( {'Cd': 0, 'ScADFa': 1, 'ScADF': 2, np.nan: 3, 'Cr': 4, 'C': 5, 'Sr': 6, 'Hc': 7, 'SchCAR': 8, 'ScACDcCF': 9, 'ScADCcCF': 10, '^hC': 11, 'ScACF': 12, 'ScACDcCcF': 13, 'S': 14, '^hCadcCfA': 15, '^r': 16, 'ScADCcCcF': 17, 'A': 18, 'R': 19, 'ScACDcCcCF': 20, 'SchCADfaF': 21, 'SchCADadfF': 22, 'SchCADaFdfR': 23, 'SchCADaFdR': 24, 'SchCADaFdRf': 25, 'HrCr': 26, 'HrC': 27, 'RR': 28})  #"ScADF":15
        #设置conn_state
        df["conn_state"] = df["conn_state"].replace({'SHR': 0, 'SH': 1, 'OTH': 2, 'RSTRH': 3, 'REJ': 4, 'RSTO': 5, 'S0': 6, 'SF': 7})  #'SH':4
       
       
        df = df.drop([" ","uid","ts","id.orig_h","id.resp_h","duration","local_resp","local_orig","orig_bytes","tunnel_parents","missed_bytes","resp_bytes"], axis=1)
        
        print("Parsed DataFrame:")
        print(df.info())

        # 进行预测
        predictions = grid_model.predict(df)

        # 返回预测结果
        result = {"predictions": predictions.tolist()}
        print( predictions)

        log_entry = {"csv_str": csv_str, "prediction": predictions.tolist()}
        log_list.append(log_entry)
        if 0 in predictions.tolist():
            send_alert_email()

        return jsonify(result)
    
    except Exception as e:
        print("exception",e)
        return jsonify({"error": str(e)}), 400

@app.route('/log_view', methods=['GET'])
def log_view():
    return render_template('log_view.html', logs=log_list)  # 渲染 HTML 页面，传递日志


@app.route('/log', methods=['GET'])
def get_logs():
    return jsonify(log_list)  # 返回所有日志



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
