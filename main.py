import json
import os
import re
import subprocess
import time

STORAGE_PATH = '/download'
DATA_FILE = '/etc/ydl/data.json'
DOWNLOAD_FILE = '/etc/ydl/download.json'

ydl_path = None

def download_video(youtube_id, path):
  subprocess.Popen(
    'youtube-dl -icw --add-metadata -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" -o "%(title)s.%(ext)s" https://youtu.be/{}'.format(youtube_id), 
    shell=True, cwd=path, stdout=subprocess.PIPE).stdout.read()

def download_music(youtube_id, path):
  subprocess.Popen(
    'youtube-dl -icw --add-metadata --extract-audio --audio-format mp3 --embed-thumbnail -o "%(title)s.%(ext)s" https://youtu.be/{}'.format(youtube_id),
    shell=True, cwd=path, stdout=subprocess.PIPE).stdout.read()

def download_playlist(data, name, is_video, playlist, path):
  res = subprocess.Popen(
    'youtube-dl --flat-playlist --skip-download -j "%s"'%playlist,
    shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').strip()
  res = '[%s]'%(','.join(res.split('\n')))
  info = json.loads(res)
  ids = list(map(lambda x: x['id'], info))
  infomap = {}
  for fo in info:
    infomap[fo['id']] = fo
  
  data_ids = []
  if name in data['playlist']:
    data_ids = list(map(lambda x: x['id'], data['playlist'][name]))
  else:
    data['playlist'][name] = []
  
  for youtube_id in ids:
    if youtube_id in data_ids:
      print(youtube_id, 'is already downloaded...')
      continue
    
    try:
      if is_video:
        print('Download video', youtube_id)
        download_video(youtube_id, path)
      else:
        print('Download music', youtube_id)
        download_music(youtube_id, path)
      data['playlist'][name].append(infomap[youtube_id])
    except Exception as e:
      print('[Error] Cannot download', youtube_id)
      print(e)


def refine_file_name(name):
  return re.sub('[\\*\\\\/"\\?:<>|]+', ' ', name)


def main():
  # load data.json
  data = {'playlist': {}}
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
      data = json.load(f)
  
  # load download.json
  with open(DOWNLOAD_FILE, 'r') as f:
    download = json.load(f)
  
  # download playlist
  for d in download['download']:
    print('Start download playlist', d['name'])
    dpath = os.path.join(STORAGE_PATH, refine_file_name(d['name']))
    
    if not os.path.exists(dpath):
      print('Make directory', dpath)
      os.makedirs(dpath)
      
    download_playlist(data, d['name'], d['is_video'], d['playlist'], dpath)
    
    # save data
    print('Write data into', DATA_FILE)
    with open(DATA_FILE, 'w') as f:
      json.dump(data, f)

if __name__ == "__main__":
  while True:
    try:
      main()
      print('Wait 30min...')
      print('\n')
      time.sleep(1800)
    except KeyboardInterrupt:
      break
  print('Program closed...')
