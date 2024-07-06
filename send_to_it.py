import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from datetime import datetime, timedelta, timezone
import ssl
import configparser

# 讀取配置文件
config = configparser.ConfigParser()
config.read('send_to_user_it.ini')

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
ADMIN_EMAIL = config.get('SMTP', 'admin_email')

# 函數：發送郵件
def send_admin_email(to_address, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = formataddr(('Admin', SMTP_ACCOUNT))
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    if attachment_path:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_path.split("/")[-1]}',
            )
            msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(SMTP_ACCOUNT, SMTP_PASSWORD)
            server.sendmail(SMTP_ACCOUNT, to_address, msg.as_string())
        print("SMTP 伺服器連接和身份驗證成功")
        print(f"郵件已發送至管理員 {to_address}")
    except Exception as e:
        print(f"SMTP 伺服器連接或身份驗證失敗: {e}")

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
        
        users_info = ""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"程式執行時間: {current_time}\n")
            f.write("------\n\n")
            f.write("即將到期的AD密碼用戶信息：\n")
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
                        users_info += user_info

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
        subject = "【AD密碼到期檢查小工具】即將到期的AD密碼用戶訊息報告"
        body = (
            f"<p>程式執行日期: {current_time}</p>"
            "<p>以下是即將到期的AD密碼用戶訊息列表：</p>"
            f"<pre>{users_info}</pre>"
            "<p>詳情請參見附件(請用文字檔打開附件即可)。</p>"
        )
        send_admin_email(ADMIN_EMAIL, subject, body, report_path)

if __name__ == "__main__":
    main()
