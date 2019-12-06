import json
import os
import re
import subprocess

URLS_TO_DOWNLOAD = [
    # name, is_video, playlist, path
    ('cassic2019',  False, 'https://www.youtube.com/playlist?list=PLK4LVBiADYBneFSVyHrFBRFXyK236tGX9', '/mnt/d/Music/2019/classic2019'),
    ('music2019-3', False, 'https://www.youtube.com/playlist?list=PLK4LVBiADYBnw7IWXiFCdjRYVz5Zz83rz', '/mnt/d/Music/2019/music2019-3'),
    ('MV2019',      True , 'https://www.youtube.com/playlist?list=PLK4LVBiADYBmnz8MIy9ppxFZytodB9YTT', '/mnt/d/Music/2019/MV2019'),
    ('Later',       True , 'https://www.youtube.com/playlist?list=PLK4LVBiADYBk_ARjq6DaGvckitGussMRi', '/mnt/e/Video/Youtube_e'),
]

DATA_FILE = './data.json'

ydl_path = None

def download_video(youtube_id, path):
    subprocess.Popen(
        '%s -icw --add-metadata -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" --ffmpeg-location /usr/local/bin/ffmpeg "https://youtu.be/%s"'%(ydl_path, youtube_id), 
        shell=True, cwd=path, stdout=subprocess.PIPE).stdout.read()

def download_music(youtube_id, path):
    subprocess.Popen(
        '%s -icw --add-metadata --extract-audio --audio-format mp3 --embed-thumbnail --ffmpeg-location /usr/local/bin/ffmpeg "https://youtu.be/%s"'%(ydl_path, youtube_id), 
        shell=True, cwd=path, stdout=subprocess.PIPE).stdout.read()

def download_playlist(data, name, is_video, playlist, path):
    res = subprocess.Popen(
        '%s --flat-playlist --skip-download -j "%s"'%(ydl_path, playlist), 
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
        except:
            print('[Error] Cannot download', youtube_id)

def main():
    # get youtube-dl path
    try:
        global ydl_path
        ydl_path = subprocess.Popen(
            'whereis youtube-dl', shell=True, stdout=subprocess.PIPE
            ).stdout.read().decode('utf-8').strip()[12:]
        print('Find youtube-dl path:', ydl_path)
    except:
        print('Cannot find youtube-dl installed. Please call `sudo pip install youtube-dl` or `sudo pip3 install youtube-dl`.')
        return
    
    # load data
    data = {'playlist': {}}
    if os.path.exists(DATA_FILE):
        print('Load data from', DATA_FILE)
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    
    # download playlist
    for name, is_video, playlist, path in URLS_TO_DOWNLOAD:
        print('Start download playlist', name)
        download_playlist(data, name, is_video, playlist, path)
        
        # save data
        print('Write data into', DATA_FILE)
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    main()
