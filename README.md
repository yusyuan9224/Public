# Windows AD Password Expiry Notification Tool

This tool is designed to automate the process of checking for users whose passwords are about to expire in Windows AD and notifying them to change their passwords. This helps reduce the workload of IT personnel who manually notify users, ensuring system security and timely password updates.

## Features

1. Search for users in Windows AD whose passwords are about to expire.
2. Generate a report and send it to the administrator.
3. Automatically send notification emails to users whose passwords are about to expire.

## Requirements

- Python 3.x
- `ldap3` module
- `smtplib` module

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/yourusername/ad-password-notify.git
    ```
2. Install the required Python packages:
    ```sh
    pip install ldap3
    ```

## Configuration

Before using this tool, configure the `settings.ini` file. Here is an example of `settings.ini`:

```ini
[LDAP]
server = ldaps://192.168.x.x
user = xxxxxx\helpdesk
password = xxxxxx
search_base = DC=xxx,DC=xxx
search_filter = (&(objectClass=user)(!(ou=離職人員))(!(userAccountControl:1.2.840.113556.1.4.803:=65536)))
attributes = sAMAccountName,mail,displayName,pwdLastSet

[SMTP]
server = smtp.office365.com
port = 587
account = xxxxxx
password = xxxxxx
admin_email = xxxxxx
```

## Usage

This tool includes two main scripts:

1. `send_to_admin.py` - Checks for users whose passwords are about to expire and generates a report to send to the administrator.
2. `send_to_user.py` - Checks for users whose passwords are about to expire and sends notification emails to the users.

### Running the Scripts

You can schedule these two scripts to run automatically to perform regular checks and send notifications.

#### Running `send_to_admin.py`

```sh
python send_to_admin.py
```

#### Running `send_to_user.py`

```sh
python send_to_user.py
```

## Contributing

Contributions are welcome. Please fork this repository, create a new branch, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Disclaimer:** This tool is for academic research and internal use only. We are not responsible for any loss or damage caused by using this tool.

# Windows AD 密碼到期通知工具

此工具旨在自動化檢查 Windows AD 上密碼即將到期的用戶，並自動通知用戶更改密碼。這樣可以減少 IT 人員手動通知用戶的工作量，確保系統的安全性和用戶的密碼更新。

## 功能

1. 搜索 Windows AD 上即將到期的密碼用戶。
2. 生成報告並發送給管理員。
3. 自動發送通知郵件給即將到期密碼的用戶。

## 需求

- Python 3.x
- `ldap3` 模組
- `smtplib` 模組

## 安裝

1. 克隆此倉庫：
    ```sh
    git clone https://github.com/yourusername/Windows-AD-Notification-Tool.git
    ```
2. 安裝所需的 Python 套件：
    ```sh
    pip install ldap3
    ```

## 配置

在使用此工具之前，請先配置 `settings.ini` 文件。以下是 `settings.ini` 文件範例：

```ini
[LDAP]
server = ldaps://192.168.x.x
user = xxxxxx\helpdesk
password = xxxxxx
search_base = DC=xxx,DC=xxx
search_filter = (&(objectClass=user)(!(ou=離職人員))(!(userAccountControl:1.2.840.113556.1.4.803:=65536)))
attributes = sAMAccountName,mail,displayName,pwdLastSet

[SMTP]
server = smtp.office365.com
port = 587
account = xxxxxx
password = xxxxxx
admin_email = xxxxxx
```

## 使用方法

此工具包含兩個主要程序：

1. `send_to_admin.py` - 檢查即將到期的密碼用戶並生成報告，發送給管理員。
2. `send_to_user.py` - 檢查即將到期的密碼用戶並發送通知郵件給用戶。

### 執行程序

可以將這兩個程序加入到排程中，自動化檢查和發送通知。

#### 執行 `send_to_admin.py`

```sh
python send_to_admin.py
```

#### 執行 `send_to_user.py`

```sh
python send_to_user.py
```

## 貢獻

歡迎對此項目進行貢獻。請先 fork 此倉庫，創建您的分支，進行修改，然後提交 pull request。

## 許可

此項目採用 MIT 許可證。詳情請參見 [LICENSE](LICENSE) 文件。

---

**免責聲明：** 此工具僅供學術研究和內部使用，不對因使用此工具導致的任何損失或損害負責。
