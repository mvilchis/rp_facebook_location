FROM revolutionsystems/python:3.6.3-wee-optimized-lto

RUN apt-get update -qq && apt-get install -y locales -qq
ENV LC_ALL="en_US.UTF-8"
ENV LC_CTYPE="en_US.UTF-8"
RUN dpkg-reconfigure locales
COPY requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT ["bash"]
CMD ["./start.sh"]
