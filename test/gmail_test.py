import smtplib
from email.mime.text import MIMEText

GMAIL_USER = ""
GMAIL_APP_PASSWORD = ""

to_email = ""

msg = MIMEText("Python에서 Gmail로 발송한 테스트 메일입니다.", "plain", "utf-8")
msg["Subject"] = "Python Gmail 발송 테스트"
msg["From"] = GMAIL_USER
msg["To"] = to_email

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    smtp.send_message(msg)

print("메일 발송 완료")

# 성공