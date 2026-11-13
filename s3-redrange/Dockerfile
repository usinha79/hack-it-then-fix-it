FROM python:3.12-slim
WORKDIR /range
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY redrange redrange
ENV PORT=5000
EXPOSE 5000
CMD ["python", "-c", "from redrange.app import app; app.run(host='0.0.0.0', port=5000, threaded=True)"]
