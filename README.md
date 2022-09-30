# 720dl
# V2 - WORK IN PROGRESS

Webcrawler for 720pier.ru which downloads ALL torrentfiles from a given overview (seachresult, Category etc.) link or from RSS-Feeds.
Doesn't re-download old torrents.

## Needs:
- pdm (https://github.com/pdm-project/pdm)

## Features:
- Monitor 720pier.ru for new torrents
- Send torrents to QBittorrent

## Installation:
- clone the repo
- pdm init
- pdm install
- edit 720pier.ru.ini to your needs
- run python 720pdl.py

## Docker:
- If you know what you are doing, the Dockerfile is included

## 720pier.ru.ini
[Default]
- savedir = Directoy to save the torrents to
- url = if RSS is not used, this link from the forum is used to download torrents
- useRSS = yes/no
- categories = comma separated list of 720pier.ru categories. "48" is "NHL" for example
- skipOlderThan = if the RSS entry is older than this, it's skipped. Format YYYY-MM-DD
- include = coma separated list of searchterms, if found this torrent is included.
- exclude = coma separated list of searchterms, if found this torrent is excluded.

[Credentials]
- username = 720pier.ru username
- password = 720pier.ru password

[Torrent]
- sendToQBittorrent = yes/no
- qbclient = URL from your QBittorrent Webview
- category = category the downloads should be put into
- startPaused = yes/no
- login = Qbittorrent Webview Login ('admin' if not changed)
- password =  Qbittorrent Webview Password ('admin' if not changed)
- BasicAuthLogin = If your Qbittorrent Webview is behind a proxy
- BasicAuthPassword = If your Qbittorrent Webview is behind a proxy
