# Mail Bill Helper

This project is a Flask-based web application that helps manage and process email bills, specifically credit card consumption bills. It integrates with the Lark (Feishu) Bitable API for data storage and retrieval.

English | [中文](README_CN.md)

---

## Features

- Crawl and process email bills from a specified label
- Store bill information in Lark Bitable
- Provide API endpoints for bill management and retrieval
- Web interface for easy interaction with the application

Note: Currently, only China Merchants Bank bill emails are supported for parsing.

## Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mail-helper-flask.git
   cd mail-helper-flask
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Obtain OAuth 2.0 credentials from the Google API Console:
   - Visit the [Google API Console](https://console.developers.google.com/).
   - Create a new project or select an existing one.
   - Go to the Credentials page and click "Create credentials" > "OAuth client ID".
   - Select "Web application" as the application type.
   - Set the authorized redirect URIs (e.g., `https://yourdomain.com/api/mailhelper/set_token`).
   - Download the client configuration and save it as `conf/cs.json` in your project directory.

   For more detailed instructions, refer to the [Google Identity documentation](https://developers.google.com/identity/protocols/oauth2).

2. Get Lark (Feishu) app credentials:
   - Log in to the [Lark developer console](https://open.feishu.cn/app).
   - Create a new app or select an existing one.
   - Go to the app's settings and find the App ID and App Secret.
   - Copy `conf.example.yaml` to `conf.yaml`:
     ```
     cp conf.example.yaml conf.yaml
     ```
   - Edit `conf.yaml` and fill in your Lark App ID and App Secret:
     ```yaml
     lark:
       app_id: your_lark_app_id
       app_secret: your_lark_app_secret
     ```

3. Clone the Bitable template:
   - Open the [Bitable template](https://isyab7gx01.feishu.cn/base/bascn26CqKFxBm55vZYrHlSsRhv?from=from_copylink)
   - Click on "Copy Base" to create your own copy
   - After cloning, go to your new Bitable's settings to find the Base ID, Table ID, and App Token
   - Add these IDs to your `conf.yaml`:
     ```yaml
     lark:
       app_id: your_lark_app_id
       app_secret: your_lark_app_secret
       base_id: your_base_id
       table_id: your_table_id
       app_token: your_app_token
     ```

4. (Optional) Set up Redis for token storage:
   - If you want to use Redis to store tokens for handling disconnection cases, set up a Redis instance.
   - Add the Redis configuration to your `conf.yaml`:
     ```yaml
     redis:
       host: your_redis_host
       port: your_redis_port
       password: your_redis_password
     ```

5. Ensure your `conf.yaml` is properly configured with all necessary settings.

6. Configure your Gmail auto-label:
   - In your Gmail settings, create a new label for credit card bills (e.g., "Credit Card Bills").
   - Set up a filter to automatically apply this label to incoming credit card bill emails.
   - Add the label name to your `conf.yaml`:
     ```yaml
     gmail:
       bill_label: "Credit Card Bills"
       email_address: your_email@gmail.com
       user_id: your_user_id
     ```

7. Enable and open bill emails in China Merchants Bank app:
   - Open the China Merchants Bank mobile app
   - Go to the settings and enable email notifications for credit card bills
   - Ensure that the bills are being sent to the Gmail account you've configured

## Usage

### Running Locally

1. Set the Flask application:
   ```
   export FLASK_APP=src/index.py
   ```

2. Run the Flask application:
   ```
   flask run
   ```

3. Access the application at `http://localhost:5000`

### Running with Docker

1. Build the Docker image:
   ```
   docker build -t mail-helper-flask .
   ```

2. Run the Docker container:
   ```
   docker run -p 5000:5000 -v $(pwd)/conf:/app/conf --name mail-helper-container mail-helper-flask
   ```

   This command does the following:
   - Maps port 5000 of the container to port 5000 on the host
   - Creates a volume that maps the local `conf` directory to `/app/conf` in the container
   - Names the container `mail-helper-container`
   - Uses the `mail-helper-flask` image we built in step 1

3. Access the application at `http://localhost:5000`

Note: Ensure that your `conf` directory contains the necessary configuration files (`conf.yaml` and `cs.json`) before running the Docker container. This volume mapping allows you to update the configuration without rebuilding the image.

## API Endpoints

- `/api/mailhelper/status`: Get the current status of the application
- `/api/mailhelper/crawl`: Initiate the bill crawling process
- `/api/mailhelper/recent_bills`: Retrieve recent bill information
- `/api/mailhelper/set_token`: Set authentication token

## Project Structure

```
mail-helper-flask/
├── src/
│   ├── index.py
│   ├── table.py
│   ├── mail.py
│   └── mycredential.py
├── static/
│   └── index.html
├── requirements.txt
├── Dockerfile
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

If you encounter any problems while using this application or have ideas to improve the user experience, a new issue is welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

