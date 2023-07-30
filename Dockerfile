FROM python:3.9-slim

WORKDIR /app
COPY . /app
VOLUME /app/data
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG TOKEN
ENV TOKEN=$TOKEN
# Set the environment variable to indicate that the application is running in Docker
ENV RUNNING_IN_DOCKER true

CMD ["python", "-u", "bot.py"]
