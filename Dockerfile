FROM python:3.12-alpine

RUN python -m venv /opt/venv

ENV PATH=/opt/venv/bin:${PATH}
ENV VIRTUAL_ENV=/opt/venv

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm /requirements.txt

COPY src /app
WORKDIR /app

CMD ["python", "main.py"]
