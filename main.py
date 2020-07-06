import json
import os
import re
import subprocess
import time

from PIL import Image

STORAGE_PATH = '/download'
DATA_FILE = '/etc/ydl/data.json'
DOWNLOAD_FILE = '/etc/ydl/download.json'

THUMB_EXTS = ['.webp', '.jpg', '.jpeg', '.png']

ydl_path = None

def download_video(youtube_id, path):
    p = subprocess.Popen(
        'youtube-dl -icw --add-metadata -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" https://youtu.be/{}'.format(youtube_id), 
        shell=True, cwd=path, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    assert stderr, 'Error occured during downloading video.'

def download_music(youtube_id, path):
    outname = os.popen('youtube-dl --get-filename -o "%(title)s.ktmp" {}'.format(youtube_id)).read().strip()
    outname = os.path.join(path, outname)
    print('outname:', outname)
    
    # download mp3 and webp file
    p = subprocess.Popen(
        'youtube-dl -icw --add-metadata --extract-audio --audio-format mp3 -o "%(title)s.ktmp.%(ext)s" {}'.format(youtube_id),
        shell=True, cwd=path, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    assert not stderr, 'Error occured during downloading mp3 file.'
    
    p = subprocess.Popen(
        'youtube-dl -icw --write-thumbnail --skip-download -o "%(title)s.ktmp.%(ext)s" {}'.format(youtube_id),
        shell=True, cwd=path, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    assert not stderr, 'Error occured during downloading thumb file.'
    
    outname_music = outname + '.mp3'
    print('outname_music:', outname_music)
    assert os.path.isfile(outname_music), 'Error occured during downloading mp3 file. File not exists.'
    
    flag = False
    for ext in THUMB_EXTS:
        outname_thumb = outname + ext
        if os.path.isfile(outname_thumb):
            flag = True
            break
    assert flag, 'Error occured during downloading thumb file. File not exists.'
    
    # convert thumb to png
    outname_thumb_png = outname + '.png'
    if not outname_thumb.endswith('.png'):
        im = Image.open(outname_thumb)
        im2 = im.convert('RGB')
        im2.save(outname_thumb_png)
        im2.close()
        im.close()
    
    # embed thumbnail to mp3 file
    outname_result = outname[:-5] + '.mp3'
    p = subprocess.Popen(
        'ffmpeg -i "%s" -i "%s" -map 0:0 -map 1:0 -c copy -id3v2_version 3'%(outname_music, outname_thumb_png) +
        ' -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" "%s"'%outname_result,
        shell=True, cwd=path, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    assert stderr, 'Error occured during embeding thumbnail.'
    
    # remove temp files
    os.remove(outname_music)
    os.remove(outname_thumb_png)
    if outname_thumb_png != outname_thumb:
        os.remove(outname_thumb)

def download_playlist(data, name, is_video, playlist, path):
    res = os.popen('youtube-dl --flat-playlist --skip-download -j "%s"'%playlist).read().strip()
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
