FROM python:3.7.13-slim

WORKDIR /app

RUN apt-get update && apt-get -y install libgomp1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose is NOT supported by Heroku
EXPOSE 8501

CMD streamlit run main.py --server.port $PORT