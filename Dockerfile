FROM python:3.8-alpine

WORKDIR /code

ENV APP app.py
ENV APP_RUN_HOST 0.0.0.0

RUN apk add --no-cache gcc musl-dev linux-headers mesa-gl

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
