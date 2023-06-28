FROM python:3.9

ADD server.py /server/
ADD requirements.txt /server/

WORKDIR /server/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1234

RUN apt-get update && apt-get install -y libgl1-mesa-glx

CMD ["python", "server.py"]