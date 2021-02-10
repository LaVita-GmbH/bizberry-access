FROM python:3.7

EXPOSE 80

COPY ./ /

RUN pip install fastapi uvicorn
RUN pip install -r requirements.txt
RUN pip install -r olympus/requirements.txt

CMD ["uvicorn", "pegasus.asgi:app", "--host", "0.0.0.0", "--port", "80"]
