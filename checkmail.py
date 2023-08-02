import os
import imaplib
from concurrent.futures import ThreadPoolExecutor
import socks
import socket
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QCheckBox
import json

def your_checking_function(email, password, ssl, proxy_address, proxy_port):
    # Thực hiện kiểm tra email sử dụng imap_server, port, ssl, proxy_address, proxy_port
    # Đây là nơi thực hiện mã kiểm tra email thông qua IMAP và proxy của bạn
    # Kết quả kiểm tra có thể là "LOGIN SUCCESS", "LOGIN FAILED" hoặc "VERIFICATION CODE"
    # Trả về kết quả kiểm tra
    return "LOGIN SUCCESS"  # Hoặc "LOGIN FAILED" hoặc "VERIFICATION CODE"

def check_mailbox(email, password, ssl, proxy_address, proxy_port):
    # Đọc dữ liệu từ tệp imap_config.json
    with open("imap_config.json", "r") as config_file:
        imap_list = json.load(config_file)

    for domain, imap_server in imap_list.items():
        if domain in email:
            # Thực hiện kiểm tra email qua IMAP với proxy
            result = your_checking_function(email, password, ssl, proxy_address, proxy_port)

            # Sau khi có kết quả, xử lý và xuất vào các tệp riêng biệt
            if "LOGIN SUCCESS" in result:
                with open("login_success.txt", "a") as login_success_file:
                    login_success_file.write(f"{email}:{password}\n")
            elif "LOGIN FAILED" in result:
                with open("login_failed.txt", "a") as login_failed_file:
                    login_failed_file.write(f"{email}:{password}\n")
            elif "VERIFICATION CODE" in result:
                with open("verification_code.txt", "a") as verification_code_file:
                    verification_code_file.write(f"{email}:{password}\n")
            break

def browse_file():
    file_path, _ = QFileDialog.getOpenFileName(None, "Chọn tệp", "", "Text files (*.txt)")
    if file_path:
        entry_file_path.setText(file_path)

def browse_proxy_file():
    proxy_file_path, _ = QFileDialog.getOpenFileName(None, "Chọn tệp proxy", "", "Text files (*.txt)")
    if proxy_file_path:
        entry_proxy_file.setText(proxy_file_path)

def start_checking():
    folder_path = entry_folder_path.text()
    file_path = entry_file_path.text()
    port = int(entry_port.text())
    ssl = checkbox_ssl.isChecked()
    max_workers = int(entry_max_workers.text())
    proxy_file_path = entry_proxy_file.text()  # Đường dẫn tệp proxy

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(proxy_file_path, 'r') as proxy_file:
        proxies = proxy_file.read().strip().splitlines()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for line in proxies:
            proxy_address, proxy_port = line.split(':')
            proxy_port = int(proxy_port)

            with ThreadPoolExecutor(max_workers=1) as email_executor:
                for email in lines:
                    email = email.strip()  # Loại bỏ các khoảng trắng và ký tự xuống dòng
                    email_executor.submit(check_mailbox, email, "", ssl, proxy_address, proxy_port)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Kiểm tra email qua IMAP với proxy")
    window.setGeometry(100, 100, 400, 300)

    # Tạo các thành phần giao diện
    central_widget = QWidget()
    layout = QVBoxLayout()

    label_folder_path = QLabel("Đường dẫn thư mục:")
    entry_folder_path = QLineEdit()
    layout.addWidget(label_folder_path)
    layout.addWidget(entry_folder_path)

    label_file_path = QLabel("Tệp chứa danh sách email và mật khẩu:")
    entry_file_path = QLineEdit()
    btn_browse = QPushButton("Chọn tệp")
    btn_browse.clicked.connect(browse_file)
    layout.addWidget(label_file_path)
    layout.addWidget(entry_file_path)
    layout.addWidget(btn_browse)

    label_port = QLabel("Cổng:")
    entry_port = QLineEdit()
    layout.addWidget(label_port)
    layout.addWidget(entry_port)

    checkbox_ssl = QCheckBox("Sử dụng SSL")
    layout.addWidget(checkbox_ssl)

    label_proxy_file = QLabel("Tệp chứa danh sách proxy:")
    entry_proxy_file = QLineEdit()
    btn_browse_proxy = QPushButton("Chọn tệp proxy")
    btn_browse_proxy.clicked.connect(browse_proxy_file)
    layout.addWidget(label_proxy_file)
    layout.addWidget(entry_proxy_file)
    layout.addWidget(btn_browse_proxy)

    label_max_workers = QLabel("Số luồng tối đa:")
    entry_max_workers = QLineEdit()
    layout.addWidget(label_max_workers)
    layout.addWidget(entry_max_workers)

    btn_start = QPushButton("Bắt đầu kiểm tra")
    btn_start.clicked.connect(start_checking)
    layout.addWidget(btn_start)

    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)

    window.show()
    sys.exit(app.exec_())
