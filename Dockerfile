FROM ubuntu:16.04
MAINTAINER Randy Reed "reedrw@appstate.edu"
RUN apt-get update -y &&\
    apt-get install -y python-pip python-dev libmysqlclient-dev
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN git clone https://github.com/mrcinv/moodle_api.py.git
RUN mv moodle_api.py moodle_apipy
RUN cp moodle_apipy/moodle_api.py .


COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
