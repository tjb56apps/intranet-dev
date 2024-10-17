FROM python:3.12

WORKDIR /home

RUN apt update && apt upgrade -y
RUN apt update && apt install vim -y

COPY . ./

# RUN chmod -R 777 /home

RUN python -m pip install -U pip
RUN pip install -r requirements.txt

CMD flask run --debug --host 0.0.0.0 --port 5000