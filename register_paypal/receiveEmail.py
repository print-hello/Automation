from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
import json
import re


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def print_info(msg, indent=0):
    global login_url
    login_url = ''
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            # print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            # print('%spart %s' % ('  ' * indent, n))
            # print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
            break
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
                # print(content)
                try:
                    login_url = re.search(
                        r'[a-zA-z]+://www.paypal.com.*signin[^\s]*sys', str(content)).group()
                except:
                    login_url = 'No email'
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))


def get_url(email, email_pwd):
    # 连接到POP3服务器:
    server = poplib.POP3_SSL('pop.mail.yahoo.com')
    server.set_debuglevel(0)
    server.user(email)
    server.pass_(email_pwd)
    print('Messages: %s. Size: %s' % server.stat())
    resp, mails, octets = server.list()
    index = len(mails)
    resp, lines, octets = server.retr(index)
    msg_content = b'\r\n'.join(lines).decode()
    msg = Parser().parsestr(msg_content)
    print_info(msg)
    # print(login_url)
    server.quit()
    return login_url