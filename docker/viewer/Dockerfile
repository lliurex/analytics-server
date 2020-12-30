FROM python:3-alpine
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && apk add curl
#CMD ["python","/app/main.py"]
