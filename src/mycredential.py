from threading import Thread
import threading
from flask import Flask, request, jsonify
import httplib2
import credential
import logging
import yaml
from oauth2client.client import OAuth2Credentials

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
from queue import Queue

# Load configuration
with open('conf/conf.yaml', 'r') as file:
    config = yaml.safe_load(file)

codeq = Queue(maxsize=1)

my_mail_address = config['gmail']['email_address']
my_user_id = config['gmail']['user_id']
my_credentials = None
auth_url = None

lock = threading.RLock()

def refresh_credentials():
    global my_credentials
    logging.info("Refreshing credentials...")
    with lock:
        logging.info("Lock acquired.")
        if my_credentials is not None and my_credentials.access_token_expired:
            try:
                logging.info("Access token expired. Refreshing...")
                http = httplib2.Http()
                my_credentials.refresh(http)
                # Store the refreshed credentials
                credential.store_credentials(my_user_id, my_credentials)
                logging.info("Credentials refreshed successfully.")
            except Exception as e:
                logging.error(f"Error refreshing credentials: {e}")
                my_credentials = None
                global auth_url
                auth_url = None

def get_credentials():
    logging.info("Getting credentials...")
    global my_credentials
    with lock:
        if my_credentials is None:
            logging.info("Credentials not found. Trying to get credentials from store...")
            my_credentials = credential.get_stored_credentials(my_user_id)
        if my_credentials is not None and my_credentials.access_token_expired:
            logging.info('Credentials expired. Refreshing...')
            refresh_credentials()
    return my_credentials

def get_credentials_or_wait(): 
    logging.info("Getting credentials or wait...")
    global my_credentials, auth_url
    with lock:
        if my_credentials is None:
            logging.info("Credentials not found. Trying to get credentials from store...")
            my_credentials = credential.get_stored_credentials(my_user_id)
        
        if my_credentials is not None:
            if my_credentials.access_token_expired:
                logging.info('Credentials expired. Refreshing...')
                refresh_credentials()
            if my_credentials is not None:
                logging.info("Credentials found and valid.")
                return my_credentials
        
        # If credentials are still None or refresh failed, proceed with the original flow
        auth_url = credential.get_authorization_url(my_mail_address, "")
        logging.info(f'auth_url: {auth_url}')
        auth_code = codeq.get()
        my_credentials = credential.get_credentials(auth_code, "")
        return my_credentials

def refresh(auth_code):
    global my_credentials
    with lock:
        my_credentials = credential.get_credentials(auth_code, "")
            
def get_credentials_or_wait_async():
    Thread(target=get_credentials_or_wait).start()

def get_auth_url() -> str:
    global auth_url
    if auth_url is not None:
        return auth_url
    else:
        auth_url = credential.get_authorization_url(my_mail_address, "")
        return auth_url

def must_get_credentials():
    global my_credentials
    with lock:
        if my_credentials is not None:
            return my_credentials
        c = credential.get_stored_credentials(my_user_id)
        if c is None: 
            raise Exception('credentials not exist in store')
        my_credentials = c
        return c

def input_token(token:str):
    if codeq.full():
        refresh(token)
        logging.info('credentials refreshed')
    else:
        codeq.put(token)

def input_token_from_stdin():
    codeq.put(input())

if __name__ == "__main__":
    t = Thread(target=input_token_from_stdin)
    t.start()
    t2 = Thread(target=get_credentials_or_wait)
    t2.start()

    app = Flask(__name__)

    @app.route('/api/set_token', methods=['GET'])
    def set_token():
        # This function is equivalent to the SetToken function in Go
        code = request.args.get('code')
        logging.info(f'code: {code}')
        if code:
            input_token(code)        
        # Return a JSON response
        return jsonify(code=0, msg="ok")

    app.run(debug=True)