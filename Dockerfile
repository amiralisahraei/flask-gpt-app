FROM  python:3.10-slim

WORKDIR /code

COPY ./requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app ./app

EXPOSE 8080

ENV GROQ_API_KEY="YOUR_GROQ_API_KEY"
ENV FLASK_APP=app/server
ENV FLASK_ENV=development

CMD [ "flask", "run", "--host=0.0.0.0", "--port=8080", "--reload" ]

