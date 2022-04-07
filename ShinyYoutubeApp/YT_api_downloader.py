"""
Skrypt pobiera dane z YouTube API i tworzy na ich podstawie pliki .csv

Potrzeba zainsalować bibliotekę do youtube api:
pip install --upgrade google-api-python-client
"""

import os
import json
import pandas as pd
import googleapiclient.discovery

############################################################################
# Konfiguracja
############################################################################
"""
FOLDER - twój folder, w którym znajduje się 'historia oglądania.json' i w którym pojawią się pliki .csv
HISTORY_FILE - nazwa pliku .json z historią
"""
FOLDER = "K_F"
HISTORY_FILE = "watch-history.json"

# inicjalizacja api
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"
# mój prywatny klucz do api, proszę nie wykorzystywać
DEVELOPER_KEY = "AIzaSyBddoiN6BgMgr_ZewEehTHcwl4Hg2F0c3c"
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)

############################################################################
# Wczytanie i utworzenie ramki danych z pliku historii
############################################################################

print("Czytanie pliku historii...")

with open(os.path.normpath(f'{FOLDER}/{HISTORY_FILE}'), encoding="utf8") as f:
    data = json.load(f)

for record in data:
    if 'header' in record:
        del record['header']
    if 'products' in record:
        del record['products']
    if 'activityControls' in record:
        del record['activityControls']
    if 'details' in record:
        del record['details']

    if 'subtitles' in record:
        record['channelName'] = record['subtitles'][0].get('name')
        record['channelUrl'] = record['subtitles'][0].get('url')
        record['channelId'] = record['channelUrl'][32:]
        del record['subtitles']

    if 'titleUrl' in record:
        record['titleId'] = record['titleUrl'][32:]

    if 'title' in record:
        record['title'] = record['title'][11:]

df = pd.DataFrame(data)
df = df.dropna()

df.to_csv(os.path.normpath(f'{FOLDER}/history.csv'), index=False)

print("Utworzono plik .csv na podstawie historii")

############################################################################
# Pobieranie danych o kanałach
############################################################################

print("Pobieranie danych o kanałach...")


def getChannelInfo(channelId):
    request = youtube.channels().list(
        part="brandingSettings,statistics",
        id=channelId
    )
    response = request.execute()
    print(response)
    return response


channels = []
for channelId in df['channelId'].unique():
    record = getChannelInfo(channelId)

    if 'items' not in record:
        continue

    record = record['items'][0]
    new_record = {
        'id': record['id'],
        'viewCount': record['statistics'].get('viewCount'),
        'subscriberCount': record['statistics'].get('subscriberCount'),
        'videoCount': record['statistics'].get('videoCount'),
        'title': record['brandingSettings']['channel']['title']
    }
    channels.append(new_record)

channelsDf = pd.DataFrame(channels)
channelsDf = channelsDf.dropna()

channelsDf.to_csv(os.path.normpath(f'{FOLDER}/channels.csv'), index=False)

print("Utworzono plik .csv z kanałami")

############################################################################
# Pobieranie danych o filmach
############################################################################

print("Pobieranie danych o filmach...")


def getVideoInfo(videoId):
    request = youtube.videos().list(
        part="statistics",
        id=videoId
    )
    response = request.execute()
    print(response)
    return response


videos = []
for titleId in df['titleId'].unique():
    record = getVideoInfo(titleId)

    if 'items' not in record or len(record['items']) == 0:
        continue

    record = record['items'][0]
    new_record = {
        'id': record['id'],
        'viewCount': record['statistics'].get('viewCount'),
        'likeCount': record['statistics'].get('likeCount'),
        'commentCount': record['statistics'].get('commentCount'),
    }
    videos.append(new_record)

videosDf = pd.DataFrame(videos)
videosDf = videosDf.dropna()

videosDf.to_csv(os.path.normpath(f'{FOLDER}/videos.csv'), index=False)
print("Utworzono plik .csv z filmami")
