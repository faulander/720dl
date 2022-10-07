# 720dl

Webcrawler for 720pier.ru which downloads torrentfiles from a given overview (seachresult, Category etc.) link or from RSS-Feeds.
Doesn't re-download old torrents. Can include or exclude searchterms and old rss entries.

## Needs:
- pdm (https://github.com/pdm-project/pdm)
- Python >= 3.10

## Features:
- Monitor 720pier.ru Website for new torrents
- Monitor 720pier.ru RSS feeds for new torrents
- Downloads the torrent files
- Send torrents to QBittorrent

## Installation:
- clone the repo
- pdm init
- pdm install
- edit 720pier.ini.yml to your needs (if 720pier.ini.yml is not there, run the program once and it will be created)
- run python 720pdl.py

## Docker:
- If you know what you are doing, the Dockerfile is included

