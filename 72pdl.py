from pathlib import Path
import requests
import apprise
import os,sys

try:
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
    from selenium.webdriver.firefox.options import Options
except ImportError:
    print("Needed module 'selenium' is not installed.")
    sys.exit(1)
try:
    import logging
    from logging import handlers
except ImportError:
    print("Needed module 'logging' is not installed.")
    sys.exit(1)
try:
    import configparser
except ImportError:
    print("Needed module 'configparser' is not installed.")
    sys.exit(1)


#Variable Definition
topics = list()
topicstovisit = list()
completedsave = list()
completed = list()
visited = bool

#Write Configs
def cfgfile():
    if len(config.read('720pier.ru.ini')) == 0:  # if config file isn't found, create it
        cfgfile = open("720pier.ru.ini", 'w')
        config.add_section('Default')
        config.add_section('Credentials')
        config.add_section('Torrent')
        config.add_section('Notification')
        config.set('Default', 'logrotate', 'True')
        config.set('Default', 'logrotatebytes', '500000')
        config.set('Default', 'rotatebackups', '5')
        config.set('Default', 'savedir', Path.cwd())
        config.set('Default', 'url', 'http://720pier.ru/search.php?search_id=active_topics&sr=topics&ot=1&pt=t&fid[]=46')
        config.set('Credentials', 'username', '<your 720pier.ru username>')
        config.set('Credentials', 'password', '<your 720pier.ru password>')
        config.set('Notification', '#Boxcar', 'boxcar://hostname')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Discord',
                   'discord://webhook_id/webhook_token')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Emby', 'emby://user@hostname/')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Boxcar', 'boxcar://hostname')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Faast',
                   'faast://authorizationtoken')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Growl',
                   'growl://password@hostname:port')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#IFTT',
                   'ifttt://webhooksID/EventToTrigger')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Join', 'join://apikey/device')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#KODI', 'kodi://hostname')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Mattermost',
                   'mmost://hostname/authkey')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Prowl', 'prowl://apikey')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Pushalot',
                   'palot://authorizationtoken')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#PushBullett', 'pbul://accesstoken')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Pushjet', 'pjet://secret')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Rocketchat',
                   'rocket://user:password@hostname/RoomID/Channel')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Slack',
                   'slack://TokenA/TokenB/TokenC/Channel')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Stride',
                   'stride://auth_token/cloud_id/convo_id')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Telegram',
                   'tgram://bottoken/ChatID')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#Twitter',
                   'tweet://user@CKey/CSecret/AKey/ASecret')  # see more @ https://github.com/caronc/apprise
        config.set('Notification', '#mailto://',
                   'mailto://userid:pass@domain.com')  # see more @ https://github.com/caronc/apprise
        config.set('Torrent', 'qbclient', 'http://127.0.0.1:8080')  # WEB-Access for qBittorrent must be available
        config.set('Torrent', 'category', '')  # no category as standard
        config.set('Torrent', 'login', 'admin')  # Login to qBittorrent Client
        config.set('Torrent', 'password', 'admin')  # Password to qBittorrent Client
        config.set('Torrent', 'download', 'True')  # Start Downloads immediately (yes/no)
        config.write(cfgfile)
        cfgfile.close()

#Pushover Example
def messaging(title,body):
    apobj = apprise.Apprise()
    if config['Notification']['Pushover']:
        apobj.add(config['Notification']['Pushover'])
        apobj.notify(
            title=title,
            body=body,
        )


#Get Configs
config = configparser.ConfigParser()
cfgfile()
config.read('720pier.ru.ini')
cfgLogrotate=config['Default']['logrotate']
cfgLogrotateBytes=int(config['Default']['logrotatebytes'])
cfgRotateBackups=config['Default']['rotatebackups']
cfgSaveDir=Path(config['Default']['savedir'])
cfgUsername=config['Credentials']['username']
cfgPassword=config['Credentials']['password']
cfgQbClient=config['Torrent']['qbclient']
cfgQbCategory=config['Torrent']['category']
cfgQbUsername=config['Torrent']['username']
cfgQbPassword=config['Torrent']['password']
cfgQbDownload=config['Torrent']['download']

# Read already finished Crawls
fileCompleted = "completed.txt"
with open(fileCompleted) as foCompleted:
    for line in foCompleted:
        completed.append(line.rstrip())

#Setup Logging
LogFilename='720dl.log'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
loghandler = logging.handlers.RotatingFileHandler(LogFilename, maxBytes=cfgLogrotateBytes, backupCount=cfgRotateBackups)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
loghandler.setFormatter(formatter)
logger.addHandler(loghandler)


#Notification System
def messaging(title,body):
    apobj = apprise.Apprise()
    if config['Notification']['Pushover']:
        apobj.add(config['Notification']['Pushover'])
        apobj.notify(
            title=title,
            body=body,
        )

# Set Firefox Environmental Variables
options = Options();
options.set_preference("browser.download.folderList",2);
options.set_preference("browser.download.manager.showWhenStarting", False);
options.set_preference("browser.download.dir",cfgSaveDir.name);
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-bittorrent,application/octet-stream");
options.add_argument("--headless")
browser = webdriver.Firefox(firefox_options=options)
logger.info("Firefox Preferences set.")

#Login to the page
try:
    browser.get('http://720pier.ru/ucp.php?mode=login')
    assert '720pier' in browser.title
    logger.info("Loginpage opened.")
    elem = browser.find_element_by_id('username')
    elem.send_keys(cfgUsername)
    elem = browser.find_element_by_id('password')
    elem.send_keys(cfgPassword)
    elem = browser.find_element_by_name('login').click()
except:
    logger.error("Loginpage couldn't be opened")
    sys.exit(1)

#Open the Last Topics
browser.get('http://720pier.ru/search.php?search_id=active_topics&sr=topics&ot=1&pt=t&fid[]=46')
#browser.get('http://720pier.ru/viewforum.php?f=88')

#Find all Topics and their Links
topics = browser.find_elements_by_class_name('topictitle')
for topic in topics:
    for c in completed:
        if c==str(topic.get_attribute('href')):
            visited=True
            completedsave.append(c)
            logger.info("Topic has already been visited: %s", c)
    if not visited:
        topicstovisit.append(topic.get_attribute('href'))
        completedsave.append(topic.get_attribute('href'))
        logger.info("Topic added to list: %s", topic.get_attribute('href'))
    visited=False

#Open Topics and download the torrent file
for topic in topicstovisit:
    browser.get(topic)
    logger.info('Trying: %s', topic)
    try:
        dl = browser.find_element_by_xpath('//*[@title="Download torrent"]').click()
        logger.info('Torrent extracted from: %s', topic)
        messaging("New Torrent", "New torrent extracted.")
    except:
       logger.error("No new Download found in: %s", str(topic))

#Write the completed file
with open(fileCompleted, "w") as foCompleted:
    for i in reversed(completedsave):
        foCompleted.writelines(i + "\n")
foCompleted.close()
browser.quit()
logger.info("Browser closed.")
