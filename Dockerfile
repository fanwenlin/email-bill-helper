# 使用官方Python运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制必要的文件和目录
COPY src/ /app/src/
COPY static/ /app/static/
COPY requirements.txt /app/

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/index.py
ENV FLASK_RUN_HOST=0.0.0.0

# Add this line to include the src directory in the Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# 暴露端口5000供Flask使用
EXPOSE 5000

# 运行Flask应用
CMD ["flask", "run"]
