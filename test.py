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

send_alert_email()
