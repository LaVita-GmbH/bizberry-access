FROM python:3.7

EXPOSE 5000
EXPOSE 5678

COPY ./ /

RUN pip install fastapi uvicorn
RUN pip install -r requirements.txt

CMD ["uvicorn", "pegasus.asgi:app", "--host", "0.0.0.0", "--port", "5000"]
