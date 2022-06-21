FROM python:3.9.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY ./Pipfile* /app/
RUN pip install pipenv
RUN pipenv lock --keep-outdated --requirements > requirements.txt
RUN pip install -r requirements.txt
COPY ./source /app
EXPOSE 8002
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8002
