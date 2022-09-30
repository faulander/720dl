# 720dl
# V2 - WORK IN PROGRESS

Webcrawler for 720pier.ru which downloads ALL torrentfiles from a given overview (seachresult, Category etc.) link.
Doesn't re-download old torrents.

##Needs:
- pdm (https://github.com/pdm-project/pdm)

## Installation:
- clone the repo
- pdm init
- pdm install
- edit 720pier.ru.ini to your needs
- run python 72pdl.py

## Docker:
- Coming

## Features:
- Monitor 720pier.ru for new torrents
- Send torrents to QBittorrent
- Monitor Ratio on sent torrents