FROM python

USER root

# Using apt-get mirror site - mirror.kakao.com: South Korea
RUN sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y atomicparsley
RUN apt-get install -y ffmpeg

RUN pip3 install --upgrade pip
RUN pip3 install youtube-dl

RUN mkdir /app
COPY ./run.sh           /app
COPY ./main.py          /app

VOLUME ["/download", "/etc/ydl"]

# Return back source.list
RUN sed -i 's/mirror.kakao.com/deb.debian.org/g' /etc/apt/sources.list

WORKDIR /app
#ENTRYPOINT ["pip3", "install", "--upgrade", "youtube-dl"]
CMD ["/app/run.sh"]
