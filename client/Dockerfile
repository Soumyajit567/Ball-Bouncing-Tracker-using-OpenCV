FROM python:3.9

ADD client.py /client/
ADD requirements.txt /client/

WORKDIR /client/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1234

RUN apt-get update && apt-get install -y libgl1-mesa-glx

CMD ["python", "client.py"]