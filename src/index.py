from datetime import datetime, timedelta
import logging
from flask import Flask, jsonify, render_template, request
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

import mail
import table
import mycredential


# Load configuration
with open('conf/conf.yaml', 'r') as file:
    config = yaml.safe_load(file)

mycredential.get_credentials_or_wait_async()

app = Flask(__name__, template_folder='../static', static_folder='../static')

# Set up scheduler for periodic refresh
scheduler = BackgroundScheduler()
scheduler.add_job(mycredential.refresh_credentials, 'interval', minutes=30)

# Add new scheduler for automatic crawling
def auto_crawl():
    label_name = config['gmail']['bill_label']
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    try:
        mail.crawl_mail(label_name, start_time, end_time)
    except Exception as e:
        logging.exception(f'Auto crawl exception: {e}')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/mailhelper/status', methods=['GET'])
def get_status():
    credential = mycredential.get_credentials()
    invalid = credential is None or credential.access_token_expired
    auth_url = None
    
    auth_url = mycredential.get_auth_url()
    # todo impl

    items = table.get_recent_bill_items()
    last_record = datetime.fromtimestamp(
        int(items[0]['时间'])/1000).strftime('%Y-%m-%d %H:%M')
    last_crawl = datetime.fromtimestamp(
        int(items[0]['Date Created'])/1000).strftime('%Y-%m-%d %H:%M')

    resp = {
        'valid': not invalid,
        'auth_url': auth_url,
        'last_crawl': last_crawl,
        'last_record': last_record,
    }
    return jsonify(resp)


@app.route('/api/mailhelper/crawl', methods=['GET'])
def crawl():
    # Get the label name from the configuration
    label_name = config['gmail']['bill_label']
    
    start, end = request.args.get('start'), request.args.get('end')
    start_time = datetime.strptime(start, '%Y-%m-%d')
    end_time = datetime.strptime(end, '%Y-%m-%d')
    if start_time and end_time:
        try:
            mail.crawl_mail(label_name, start_time, end_time)
        except Exception as e:
            logging.exception(f'exception {e}')
            return jsonify(code=500, message=str(e))
    else:
        return jsonify(code=400, msg=f'bad request, start:{start_time}, end:{end_time}')

    # Return a JSON response
    return jsonify(code=0, msg="success")


@app.route('/api/mailhelper/recent_bills', methods=['GET'])
def recent_bills():
    items = table.get_recent_bill_items()
    respItems = [{
        '标题': item['标题'],
        '金额':  "¥ " + item['RMB金额'] ,
        '时间': datetime.fromtimestamp(int(items[0]['时间'])/1000).strftime('%m-%d %H:%M'),
        '分类': item['一级分类'],
    } for item in items]
    resp = {
        'data': respItems,
    }
    return jsonify(resp)


@app.route('/api/mailhelper/set_token', methods=['GET'])
def set_token():
    # This function is equivalent to the SetToken function in Go
    code = request.args.get('code')
    logging.info(f'code: {code}')
    if code:
        mycredential.input_token(code)
        mail.refresh_service()
    # Return a JSON response
    return jsonify(code=0, msg="ok")


@app.route('/api/mailhelper/refresh', methods=['GET'])
def manual_refresh():
    mycredential.refresh_credentials()
    return jsonify(code=0, msg="Refresh attempt completed")

if __name__ == "__main__":
    mail.init_service_or_wait_async()
    # Set up scheduler for periodic refresh
    scheduler = BackgroundScheduler()
    scheduler.add_job(mycredential.refresh_credentials, 'interval', minutes=5)

    scheduler.add_job(auto_crawl, 'interval', hours=24)  # Run once a day

    scheduler.start()
    app.run(debug=True)
