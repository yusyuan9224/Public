import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from datetime import datetime, timedelta, timezone
import ssl
import time
import configparser

# 讀取配置文件
config = configparser.ConfigParser()
config.read('send_to_user_config.ini')

# LDAP 伺服器和連接配置
LDAP_SERVER = config.get('LDAP', 'server')
LDAP_USER = config.get('LDAP', 'user')
LDAP_PASSWORD = config.get('LDAP', 'password')
SEARCH_BASE = config.get('LDAP', 'search_base')
SEARCH_FILTER = config.get('LDAP', 'search_filter')
ATTRIBUTES = config.get('LDAP', 'attributes').split(',')

# 電子郵件發送參數配置
SMTP_SERVER = config.get('SMTP', 'server')
SMTP_PORT = config.getint('SMTP', 'port')
SMTP_ACCOUNT = config.get('SMTP', 'account')
SMTP_PASSWORD = config.get('SMTP', 'password')

# 函數：發送給客戶郵件
def send_users_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = formataddr(('Admin', SMTP_ACCOUNT))
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(SMTP_ACCOUNT, SMTP_PASSWORD)
            server.sendmail(SMTP_ACCOUNT, to_address, msg.as_string())
        print(f"郵件已發送至客戶 {to_address}")
    except Exception as e:
        print(f"發送郵件時出錯: {e}")

# 函數：搜索LDAP並生成報告
def search_ldap_and_generate_report():
    print("正在連接LDAP伺服器...")

    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=LDAP_USER, password=LDAP_PASSWORD, authentication=NTLM)
        if not conn.bind():
            print(f"LDAP伺服器連接失敗: {conn.result}")
            return None
        print("LDAP伺服器連接成功")
    except Exception as e:
        print(f"連接LDAP伺服器時出錯: {e}")
        return None

    try:
        print(f"正在搜索LDAP，搜索基礎：{SEARCH_BASE}，篩選條件：{SEARCH_FILTER}")
        conn.search(SEARCH_BASE, SEARCH_FILTER, attributes=ATTRIBUTES, search_scope=SUBTREE)

        # 當前日期
        utc8 = timezone(timedelta(hours=8))
        now = datetime.now(utc8)
        current_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")
        today_date = now.strftime("%Y-%m-%d")

        # 打印即將到期的密碼信息
        report_path = "即將到期的AD密碼用戶信息.txt"
        network_path = f"\\\\192.168.8.50\\Share\\Department\\營運支援中心\\資訊部\\mis\\AD 密碼通知信件 log\\{today_date}.txt"
        
        users_info = ""
        with open(report_path, "w", encoding="utf-8") as f, open(network_path, "w", encoding="utf-8") as net_f:
            f.write(f"程式執行時間: {current_time}\n")
            f.write("------\n\n")
            f.write("即將到期的AD密碼用戶信息：\n")
            net_f.write(f"程式執行時間: {current_time}\n")
            net_f.write("------\n\n")
            net_f.write("即將到期的AD密碼用戶信息：\n")
            users_info = ""
            for entry in conn.entries:
                if entry.pwdLastSet and entry.mail:
                    pwd_last_set_date = entry.pwdLastSet.value.replace(tzinfo=timezone.utc).astimezone(utc8)
                    pwd_expiry_date = pwd_last_set_date + timedelta(days=180)  # 假設密碼過期時間為180天
                    days_left = (pwd_expiry_date - now).days

                    if 0 < days_left <= 14:  # 即將到期
                        user_info = (
                            f"用戶: {entry.displayName.value}\n"
                            f"信箱: {entry.mail.value}\n"
                            f"密碼設定時間: {pwd_last_set_date}\n"
                            f"密碼到期時間: {pwd_expiry_date}\n"
                            f"剩餘天數: {days_left}\n"
                            "------\n"
                        )
                        f.write(user_info)
                        net_f.write(user_info)
                        users_info += user_info

                        # 發送通知郵件給需要更改密碼的用戶
                        user_subject = "【資訊部】您的Windows密碼即將到期，請立即更改!"
                        user_body = (
                            f"<p>Dear {entry.displayName.value}，</p>"
                            f"<p>您的Windows密碼將在 {days_left} 天後到期。請及時更改密碼。</p>"
                            f"<p>密碼到期時間: {pwd_expiry_date}</p>"
                            f"<p>下方連結為密碼更改教學：</p>"
                            f"<p><a href='https://example.com/change-password'>點擊這裡進行密碼更改</a></p>"
                            f"<p>BR，</p>"
                            f"<p>資訊部</p>"
                        )
                        send_users_email(entry.mail.value, user_subject, user_body)
                        time.sleep(5)  

        return report_path, users_info

    except Exception as e:
        print(f"搜索LDAP時出錯: {e}")
        return None
    finally:
        conn.unbind()

# 主程式
def main():

    # 當前日期
    utc8 = timezone(timedelta(hours=8))
    now = datetime.now(utc8)
    current_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    result = search_ldap_and_generate_report()
    if result:
        report_path, users_info = result

if __name__ == "__main__":
    main()
