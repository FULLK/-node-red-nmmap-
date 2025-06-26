import pandas as pd
import numpy as np

def access_data():
    # 假设 new_data 是你想要预测的新数据 DataFrame
    # 1. 去掉不需要的列
    new_data = new_data.drop(["id.resp_h", "service", "orig_ip_bytes", "orig_pkts", "resp_pkts"], axis=1)

    # 2. 对类别变量进行编码，使用训练时相同的映射
    new_data["service"] = new_data["service"].replace({"ntp": 0, "dns": 1, "gssapi": 2, "dns": 3})
    new_data["proto"] = new_data["proto"].map({"udp": 0, "tcp": 1})
    new_data["history"] = new_data["history"].replace({v: k for k, v in enumerate(new_data["history"].unique().tolist())})
    new_data["conn_state"] = new_data["conn_state"].replace({v: k for k, v in enumerate(new_data["conn_state"].unique().tolist())})

    # 如果有缺失值，需要先填充或删除缺失值
    new_data = new_data.dropna(axis=0)

    # 3. 确保数据列与训练数据的列对齐
    new_data = new_data[X.columns]  # 保证列名一致
