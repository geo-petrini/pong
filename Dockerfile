FROM python:3.12-alpine

EXPOSE 5000
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir uploads
# COPY blueprints .
# COPY modules .
# COPY static .
# COPY templates .
# COPY app.py .
COPY . .

CMD ["python", "app.py"]