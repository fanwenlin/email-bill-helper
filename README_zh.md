# 邮件账单助手

这是一个基于Flask的Web应用程序，用于管理和处理邮件账单，特别是信用卡消费账单。它与飞书（Lark）多维表格API集成，用于数据存储和检索。

[English](README.md) | 中文

---

## 功能

- 从指定标签抓取和处理邮件账单
- 将账单信息存储在飞书多维表格中
- 提供账单管理和检索的API端点
- 用于轻松交互的Web界面

注意：目前仅支持解析招商银行的账单邮件。

## 前提条件

- Python 3.9+
- Docker（可选，用于容器化部署）

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/mail-helper-flask.git
   cd mail-helper-flask
   ```

2. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

## 配置

1. 从Google API控制台获取OAuth 2.0凭据：
   - 访问[Google API控制台](https://console.developers.google.com/)。
   - 创建新项目或选择现有项目。
   - 转到凭据页面，点击"创建凭据" > "OAuth客户端ID"。
   - 选择"Web应用程序"作为应用程序类型。
   - 设置授权重定向URI（例如，`https://yourdomain.com/api/mailhelper/set_token`）。
   - 下载客户端配置并将其保存为项目目录中的`conf/cs.json`。

   有关更详细的说明，请参阅[Google Identity文档](https://developers.google.com/identity/protocols/oauth2)。

2. 获取飞书（Lark）应用凭据：
   - 登录[飞书开发者控制台](https://open.feishu.cn/app)。
   - 创建新应用或选择现有应用。
   - 转到应用设置并找到App ID和App Secret。
   - 复制`conf.example.yaml`到`conf.yaml`：
     ```
     cp conf.example.yaml conf.yaml
     ```
   - 编辑`conf.yaml`并填写您的飞书App ID和App Secret：
     ```yaml
     lark:
       app_id: your_lark_app_id
       app_secret: your_lark_app_secret
     ```

3. 克隆多维表格模板：
   - 打开[多维表格模板](https://isyab7gx01.feishu.cn/base/bascn26CqKFxBm55vZYrHlSsRhv?from=from_copylink)
   - 点击"复制基础"创建您自己的副本
   - 克隆后，转到新多维表格的设置以找到Base ID、Table ID和App Token
   - 将这些ID添加到您的`conf.yaml`中：
     ```yaml
     lark:
       app_id: your_lark_app_id
       app_secret: your_lark_app_secret
       base_id: your_base_id
       table_id: your_table_id
       app_token: your_app_token
     ```

4. （可选）设置Redis用于令牌存储：
   - 如果您想使用Redis存储令牌以处理断开连接的情况，请设置一个Redis实例。
   - 将Redis配置添加到您的`conf.yaml`中：
     ```yaml
     redis:
       host: your_redis_host
       port: your_redis_port
       password: your_redis_password
     ```

5. 确保您的`conf.yaml`已正确配置所有必要的设置。

6. 配置Gmail自动标签：
   - 在Gmail设置中，为信用卡账单创建一个新标签（例如，"信用卡账单"）。
   - 设置一个过滤器，自动将此标签应用于传入的信用卡账单邮件。
   - 将标签名称添加到您的`conf.yaml`中：
     ```yaml
     gmail:
       bill_label: "信用卡账单"
       email_address: your_email@gmail.com
       user_id: your_user_id
     ```

7. 在招商银行应用中启用并打开账单邮件：
   - 打开招商银行手机应用
   - 转到设置并启用信用卡账单的邮件通知
   - 确保账单正在发送到您配置的Gmail账户
   - 重要：在招商银行应用中至少打开一封账单邮件，以激活邮件通知服务

## 使用方法

### 本地运行

1. 设置Flask应用：
   ```
   export FLASK_APP=src/index.py
   ```

2. 运行Flask应用：
   ```
   flask run
   ```

3. 在`http://localhost:5000`访问应用

### 使用Docker运行

1. 构建Docker镜像：
   ```
   docker build -t mail-helper-flask .
   ```

2. 运行Docker容器：
   ```
   docker run -p 5000:5000 -v $(pwd)/conf:/app/conf --name mail-helper-container mail-helper-flask
   ```

   此命令执行以下操作：
   - 将容器的5000端口映射到主机的5000端口
   - 创建一个卷，将本地的`conf`目录映射到容器内的`/app/conf`目录
   - 将容器命名为`mail-helper-container`
   - 使用我们在步骤1中构建的`mail-helper-flask`镜像

3. 在`http://localhost:5000`访问应用

## API端点

- `/api/mailhelper/status`：获取应用程序的当前状态
- `/api/mailhelper/crawl`：启动账单抓取过程
- `/api/mailhelper/recent_bills`：检索最近的账单信息
- `/api/mailhelper/set_token`：设置认证令牌

## 项目结构

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

## 贡献

欢迎贡献！请随时提交Pull Request。

如果您在使用此应用程序时遇到任何问题，或者有改善用户体验的想法，欢迎提出新的issue。


## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
