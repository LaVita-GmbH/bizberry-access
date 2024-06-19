FROM python:3.9
EXPOSE 5000

COPY ./ /app
WORKDIR /app

RUN pip install fastapi psycopg2-binary django_cockroachdb~=4.1.0
RUN pip install -r requirements.txt
RUN pip uninstall -y httptools

CMD ["uvicorn", "bb_access.asgi:app", "--host", "0.0.0.0", "--port", "5000"]
