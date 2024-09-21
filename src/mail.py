import base64
import logging
from threading import Thread
import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup

from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import locale
from mycredential import get_credentials_or_wait, must_get_credentials

import httplib2
from table import BillItem, save_bill_items

def build_service(credentials):
  """Build a Gmail service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Gmail service object.
  """
  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('gmail', 'v1', http=http)

service = None
def must_init_service():
    global service
    service = build_service(must_get_credentials())

def init_service_or_wait():
    global service
    service = build_service(get_credentials_or_wait())

def init_service_or_wait_async():
    Thread(target=init_service_or_wait).start()

def refresh_service():
    global service
    service = build_service(must_get_credentials())

def search_mails(label_name, start_time:datetime, end_time:datetime):
    query = f'label:{label_name} after:{int(start_time.timestamp())} before:{int(end_time.timestamp())}'
    response = service.users().messages().list(userId='me', q=query).execute()
    logging.info(f'search_mails response: {response}, query: {query}')
    messages = response.get('messages', [])
    return messages

def get_mail_content(message_id):
    message = service.users().messages().get(userId='me', id=message_id).execute()
    parts = message['payload']['parts']
    
    for part in parts:
        if part['mimeType'] == "text/html":
            raw = part['body']['data']
            return base64.urlsafe_b64decode(raw).decode('utf-8')
    return ""

try:
    locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
except locale.Error:
    # Fallback to a more commonly available locale or the default locale
    try:
        locale.setlocale(locale.LC_TIME, 'C.UTF-8')
    except locale.Error:
        # If even the fallback fails, use the default locale
        locale.setlocale(locale.LC_TIME, '')

def is_table_prefix(text:str)-> bool:
    if text is None:
        print('text is none')
        return False
    else:
        
        print(f'debug check prefix, text:{text}, result:{"消费明细如下" in text}\n')
        return '消费明细如下' in text


def clean_string(s):
    """
    Clean a string by removing leading/trailing whitespace characters
    (like spaces, newline '\n', and carriage return '\r'),
    and replacing one or more consecutive internal whitespace characters
    with a single space.

    :param s: The string to be cleaned.
    :return: A cleaned version of the string.
    """
    # Remove leading/trailing whitespace characters
    s = s.strip()

    # Replace one or more consecutive internal whitespace characters with a single space
    s = re.sub(r'\s+', ' ', s)

    return s

def process_bill_email(id, html):
    soup = BeautifulSoup(html, 'html.parser')
    # span = soup.find('span', string=lambda text:text and '消费明细如下' in text)
    spans = soup.find_all('span')
    prefix_span = None
    for span in spans:
        if '消费明细如下' in span.get_text():
            prefix_span = span
            break
    

    if not prefix_span:
        return []

    items = []
    for tr in prefix_span.find_all_next('table')[0].find_all('tr'):
        text = clean_string(tr.get_text())
        date_match = re.search(r'\d{4}/\d{2}/\d{2}', text) 
        time_value_match = re.search(r'(\d{2}:\d{2}:\d{2})\s*CNY.(-?\d+\.\d*)\s*(.*)', text)

        if date_match:
            current_date = datetime.strptime(date_match.group(), '%Y/%m/%d')
        else: 
            if time_value_match:
                detail = time_value_match.group(3)         
                time_str = time_value_match.group(1)
                value_str = time_value_match.group(2)
                bill_time = datetime.strptime(time_str, '%H:%M:%S').replace(year=current_date.year, month=current_date.month, day=current_date.day)
                bill_value_cent = int(float(value_str) * 100)
                item = BillItem( bill_value_cent,  bill_time, detail, source_id=id)
                if item in items:
                    continue
                items.append(item)

    # unique items
    # items = items.
    return items

def crawl_mail(label_name: str, start_time: datetime, end_time: datetime):
    logging.info(f'crawl_mail, start_time={start_time}, end_time={end_time}')
    messages = search_mails(label_name, start_time, end_time)
    logging.info(f'mails:{messages}')

    for message in messages:
        email_content = get_mail_content(message['id'])
        bill_details = process_bill_email(message['id'], email_content)
        print(bill_details)
        save_bill_items(bill_details)
        time.sleep(0.2)
    
# 示例使用
# html_content = '...您的HTML内容...'
# bill_items = process_bill_email(html_content)
# print(bill_items)

# Example usage
if __name__ == '__main__':
    must_init_service()
    label_name = '账单/信用卡消费账单'
    start_time = (datetime.now() - timedelta(days=210)).strftime('%Y/%m/%d')
    # start_time = (datetime.now() - timedelta(days=210)).strftime('%Y/%m/%d')
    end_time = (datetime.now() - timedelta(days=130)).strftime('%Y/%m/%d')
    # end_time = datetime.now().strftime('%Y/%m/%d')
    messages = search_mails(label_name, start_time, end_time)

    for message in messages:
        email_content = get_mail_content(message['id'])
        bill_details = process_bill_email(message['id'], email_content)
        print(bill_details)
        save_bill_items(bill_details)
        time.sleep(0.2)
        # You can then save or process these bill details as needed
