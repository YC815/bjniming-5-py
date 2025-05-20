# 使用 Python 官方映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製檔案到容器中
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 設定 Flask 的環境變數
ENV FLASK_APP=main
ENV FLASK_RUN_HOST=0.0.0.0

# 開放 port
EXPOSE 5000

# 啟動 Flask 應用
CMD ["python", "-m", "flask", "run"]
