FROM python:slim
WORKDIR /app
COPY req.txt .
RUN python3 -m venv lvenv3
RUN ./lvenv3/bin/pip3 install --upgrade pip
RUN ./lvenv3/bin/pip3 install -r req.txt

COPY app/ app/
CMD ["./lvenv3/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
