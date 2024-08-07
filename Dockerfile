FROM python:3.10

ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN python3 -m venv /opt/ENVCRM

COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt

COPY . .

RUN /opt/ENVCRM/bin/pip install pip --upgrade && \
    /opt/ENVCRM/bin/pip install -r requirements.txt && \
    chmod +x entrypoint.sh

#CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000"]

#RUN /opt/ENVCRM/bin/python3 manage.py runscript fill

CMD ["/app/entrypoint.sh"]

