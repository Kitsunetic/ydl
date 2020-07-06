FROM python

USER root

# Using apt-get mirror site - mirror.kakao.com: South Korea
#RUN sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y atomicparsley
RUN apt-get install -y ffmpeg
RUN apt-get clean

#RUN pip3 --no-cache-dir install --upgrade pip
#RUN pip3 --no-cache-dir install youtube-dl
RUN git clone https://github.com/ytdl-org/youtube-dl /youtube-dl
WORKDIR /youtube-dl
RUN python setup.py install
WORKDIR /
RUN rm -r /youtube-dl

RUN mkdir /app
COPY ./run.sh           /app
COPY ./main.py          /app

VOLUME ["/download", "/etc/ydl"]

# Return back source.list
#RUN sed -i 's/mirror.kakao.com/deb.debian.org/g' /etc/apt/sources.list

WORKDIR /app
#ENTRYPOINT ["pip3", "install", "--upgrade", "youtube-dl"]
CMD ["/app/run.sh"]
