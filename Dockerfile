FROM  python:3.10-slim

WORKDIR /code


# Install MySQL client libraries
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && apt-get clean


# RUN pip install --no-cache-dir --upgrade -r requirements.txt


# Install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt 


# Clean up
RUN apt-get update \
    && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*



COPY ./app ./app

COPY ./.env ./

EXPOSE 8080

CMD [ "flask", "run", "--host=0.0.0.0", "--port=8080", "--reload" ]

