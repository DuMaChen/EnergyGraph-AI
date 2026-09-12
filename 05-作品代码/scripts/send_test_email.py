#!/usr/bin/env python3
"""SMTP Test Email Delivery and Diagnostic Utility.

Usage:
  python3 scripts/send_test_email.py --to user@example.com [--env-file deploy/.env]
  python3 scripts/send_test_email.py --to user@example.com --host ssl://smtp.qq.com:465 --user registrar_off@qq.com --password <AUTH_CODE>
"""

from __future__ import annotations

import argparse
import email.utils
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def load_env_file(filepath: str | Path) -> dict[str, str]:
    env: dict[str, str] = {}
    path = Path(filepath)
    if not path.is_file():
        return env
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k:
                env[k] = v
    return env


def parse_host_port_secure(host_raw: str, secure_override: str | None = None) -> tuple[str, int, bool]:
    """Parse host strings like ssl://smtp.qq.com:465 or smtp.qq.com:587."""
    host_str = host_raw.strip()
    is_ssl = False

    if host_str.startswith("ssl://"):
        is_ssl = True
        host_str = host_str[6:]
    elif host_str.startswith("tls://"):
        host_str = host_str[6:]

    port = 465 if is_ssl else 25
    if ":" in host_str:
        host, port_str = host_str.split(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            pass
    else:
        host = host_str

    if secure_override:
        sec = secure_override.lower().strip()
        if sec in ("ssl", "ssl/tls") or port == 465:
            is_ssl = True
        elif sec == "tls" or port == 587:
            is_ssl = False

    return host, port, is_ssl


def send_email(
    host_raw: str,
    user: str,
    password: str,
    to_addr: str,
    from_addr: str | None = None,
    subject: str = "【电力系统储能技术】邮件测试通知",
    secure_override: str | None = None,
    timeout: int = 30,
) -> bool:
    sender = from_addr or user
    if not sender:
        print("[ERROR] 发件人地址 (sender) 不能为空", file=sys.stderr)
        return False

    host, port, is_ssl = parse_host_port_secure(host_raw, secure_override)
    print(f"[*] 准备连接 SMTP 服务器: {host}:{port} (SSL: {'是' if is_ssl else '否/STARTTLS'})")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"电力系统储能技术平台 <{sender}>"
    msg["To"] = to_addr
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="energygraph.icu")

    text_body = f"""您好：

这是一封来自「电力系统储能技术」课程 Agent 平台的测试邮件。
如果您收到了这封邮件，说明平台的 SMTP 外发邮件配置已成功生效！

发信时间：{email.utils.formatdate(localtime=True)}
发信服务器：{host}:{port}
发信账号：{sender}
目标收件人：{to_addr}

祝学习与教学愉快！
电力系统储能技术教学团队
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #e1e4e8; border-radius: 8px;">
  <div style="background: linear-gradient(135deg, #1890ff, #096dd9); color: #fff; padding: 18px 24px; border-radius: 6px 6px 0 0;">
    <h2 style="margin: 0; font-size: 20px;">⚡ 电力系统储能技术课程平台</h2>
    <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 13px;">邮件服务连通性测试</p>
  </div>
  <div style="padding: 24px 16px;">
    <p>您好：</p>
    <p>这是一封来自<strong>「电力系统储能技术」课程 Agent 平台</strong>的测试邮件。</p>
    <div style="background: #f6ffed; border: 1px solid #b7eb8f; padding: 12px 16px; border-radius: 4px; color: #389e0d; margin: 16px 0;">
      ✅ <strong>SMTP 邮件外发服务已联通成功！</strong>
    </div>
    <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin: 16px 0;">
      <tr><td style="padding: 6px 0; color: #666;">发信服务器：</td><td style="padding: 6px 0; font-weight: bold;">{host}:{port}</td></tr>
      <tr><td style="padding: 6px 0; color: #666;">发件账号：</td><td style="padding: 6px 0;">{sender}</td></tr>
      <tr><td style="padding: 6px 0; color: #666;">收件账号：</td><td style="padding: 6px 0;">{to_addr}</td></tr>
      <tr><td style="padding: 6px 0; color: #666;">发送时间：</td><td style="padding: 6px 0;">{email.utils.formatdate(localtime=True)}</td></tr>
    </table>
    <p style="margin-top: 24px; color: #666; font-size: 12px; border-top: 1px solid #eee; padding-top: 12px;">
      此邮件由系统自动发送，如有疑问可联系课程管理员。
    </p>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if is_ssl or port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=timeout)
        else:
            server = smtplib.SMTP(host, port, timeout=timeout)
            print("[*] 正在执行 STARTTLS 安全握手...")
            server.starttls()

        print("[*] 连接成功，正在进行 SMTP 身份认证...")
        server.login(user, password)
        print(f"[*] 认证成功，正在投递邮件至 {to_addr} ...")
        server.sendmail(sender, [to_addr], msg.as_string())
        server.quit()
        print(f"\n[SUCCESS] 测试邮件已成功投递到 {to_addr}！")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n[ERROR] SMTP 认证失败 (535): {e}", file=sys.stderr)
        print("💡 提示：若使用 QQ 邮箱，请确认密码填写的是 16 位 SMTP 独立「授权码」，而非 QQ 账户密码。", file=sys.stderr)
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"\n[ERROR] 收件人地址被服务器拒绝: {e}", file=sys.stderr)
        return False
    except smtplib.SMTPSenderRefused as e:
        print(f"\n[ERROR] 发件人地址被服务器拒绝: {e}", file=sys.stderr)
        print(f"💡 提示：请确保发件人地址 ({sender}) 与登录用户名 ({user}) 一致或已被授权。", file=sys.stderr)
        return False
    except (smtplib.SMTPException, OSError) as e:
        print(f"\n[ERROR] 邮件发送异常: {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Moodle/课程平台 SMTP 邮件外发测试工具")
    parser.add_argument("--to", required=True, help="目标收件邮箱地址 (例如: student@qq.com)")
    parser.add_argument("--env-file", default="deploy/.env", help="环境变量配置文件路径 (默认: deploy/.env)")
    parser.add_argument("--host", help="SMTP 服务器地址 (例如: ssl://smtp.qq.com:465)")
    parser.add_argument("--user", help="SMTP 登录用户名 (例如: registrar_off@qq.com)")
    parser.add_argument("--password", help="SMTP 授权码/密码")
    parser.add_argument("--from-addr", help="发件人地址 (默认与 user 相同)")
    parser.add_argument("--secure", choices=["ssl", "tls"], help="安全加密方式")
    parser.add_argument("--subject", default="【电力系统储能技术】邮件测试通知", help="邮件主题")

    args = parser.parse_args()

    env = load_env_file(args.env_file)
    host = args.host or env.get("MOODLE_SMTP_HOST") or "ssl://smtp.qq.com:465"
    user = args.user or env.get("MOODLE_SMTP_USER") or env.get("MOODLE_NOREPLY_ADDRESS")
    password = args.password or env.get("MOODLE_SMTP_PASS")
    secure = args.secure or env.get("MOODLE_SMTP_SECURE")
    from_addr = args.from_addr or env.get("MOODLE_NOREPLY_ADDRESS") or user

    if not user or not password:
        print("[ERROR] 缺少 SMTP 登录用户名或授权码！", file=sys.stderr)
        print(f"请在 {args.env_file} 中配置 MOODLE_SMTP_USER 和 MOODLE_SMTP_PASS，或通过命令行参数 --user 和 --password 提供。", file=sys.stderr)
        return 1

    ok = send_email(
        host_raw=host,
        user=user,
        password=password,
        to_addr=args.to,
        from_addr=from_addr,
        subject=args.subject,
        secure_override=secure,
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
