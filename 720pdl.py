from pathlib import Path
import requests
import os,sys
from qbclient import Client
import logging
from logging import handlers
import configparser

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


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
        config.set('Default', 'logrotate', 'yes')
        config.set('Default', 'logrotatebytes', '500000')
        config.set('Default', 'rotatebackups', '5')
        config.set('Default', 'savedir', str(Path.cwd()))
        config.set('Default', 'url', 'http://720pier.ru/search.php?search_id=active_topics&sr=topics&ot=1&pt=t&fid[]=46')
        config.set('Credentials', 'username', '<your 720pier.ru username>')
        config.set('Credentials', 'password', '<your 720pier.ru password>')
        config.set('Torrent', 'sendToQBittorrent', "no")
        config.set('Torrent', 'qbclient', 'http://127.0.0.1:8080')  # WEB-Access for qBittorrent must be available
        config.set('Torrent', 'category', '')  # no category as standard
        config.set('Torrent', 'login', 'admin')  # Login to qBittorrent Client
        config.set('Torrent', 'password', 'admin')  # Password to qBittorrent Client
        config.set('Torrent', 'download', 'yes')  # Start Downloads immediately (yes/no)
        config.set('Torrent', 'stopAtRatio', '-1')  # Start Downloads immediately (yes/no)
        config.set('Torrent', 'stopAtTime', '-1')  # Start Downloads immediately (yes/no)

        config.write(cfgfile)
        cfgfile.close()

#Get Configs
config = configparser.ConfigParser()
cfgfile()
config.read('720pier.ru.ini')
cfgLogrotate=config['Default'].getboolean('logrotate')
cfgLogrotateBytes=int(config['Default']['logrotatebytes'])
cfgRotateBackups=config['Default']['rotatebackups']
cfgSaveDir=Path(config['Default']['savedir'])
cfgUsername=config['Credentials']['username']
cfgPassword=config['Credentials']['password']
cfgSendToQb=config['Torrent'].getboolean('sendToQBittorrent')
cfgQbClient=config['Torrent']['qbclient']
cfgQbCategory=config['Torrent']['category']
cfgQbUsername=config['Torrent']['login']
cfgQbPassword=config['Torrent']['password']
cfgQbDownload=config['Torrent']['download']

# Read already finished Crawls
fileCompleted = "completed.txt"
try:
    with open(fileCompleted, "r") as foCompleted:
        for line in foCompleted:
            completed.append(line.rstrip())
except FileNotFoundError:
    open(fileCompleted, "x")

#Setup Logging
LogFilename='720dl.log'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
loghandler = logging.handlers.RotatingFileHandler(LogFilename, maxBytes=cfgLogrotateBytes, backupCount=cfgRotateBackups)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
loghandler.setFormatter(formatter)
logger.addHandler(loghandler)

if cfgUsername == "<your 720pier.ru username>":
    print("Please adapt 720pier.ru.ini to your needs")
    sys.exit(1)

if cfgSendToQb == True:
    qb = Client(cfgQbClient)
    qb.login(cfgQbUsername, cfgQbPassword)
    # try:
    #     torrents = qb.torrents()
    #     for torrent in torrents:
    #         logger.info(torrent['name'])
    # except Exception as e:
    #     logger.error(e)
    #     sys.exit(1)
    

# Set Firefox Environmental Variables
options = Options()
options.set_preference("browser.download.dir", os.path.abspath(os.path.dirname(__file__)))
#options.set_preference("browser.download.dir", cfgSaveDir.name)
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.helperApps.neverAsk.saveToDisk","application/x-bittorrent,application/octet-stream")
options.set_preference("browser.helperApps.neverAsk.openFile","application/x-bittorrent,application/octet-stream")
options.set_preference("browser.download.manager.addToRecentDocs", False)
options.set_preference("browser.helperApps.alwaysAsk.force", False)
options.set_preference("browser.download.alwaysOpenPanel", False)
options.set_preference("browser.download.panel.shown", False)
options.add_argument("--headless")
#options.add_argument("");
browser = webdriver.Firefox(options=options)
logger.info("Firefox Preferences set.")


#Login to the page
try:
    browser.get('https://720pier.ru/ucp.php?mode=login')
    assert '720pier' in browser.title
    logger.info("Loginpage opened.")
    elem = browser.find_element(By.ID,'username')
    elem.send_keys(cfgUsername)
    elem = browser.find_element(By.ID,'password')
    elem.send_keys(cfgPassword)
    elem = browser.find_element(By.NAME,'login').click()
except Exception as e:
    if hasattr(e, 'message'):
        logger.error(e.message)
    else:
        logger.error(e)
    sys.exit(1)

browser.implicitly_wait(0.5)

try:
    #Open the Last Topics
    browser.get('http://720pier.ru/search.php?search_id=active_topics&sr=topics&ot=1&pt=t&fid[]=46')
    #browser.get('http://720pier.ru/viewforum.php?f=88')
except Exception as e:
    if hasattr(e, 'message'):
        logger.error(e.message)
    else:
        logger.error(e)
    sys.exit(1)


#Find all Topics and their Links
topics = browser.find_elements(By.CLASS_NAME,'topictitle')
for topic in topics:
    logger.debug(topic)
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
        dl = browser.find_element(By.XPATH,'//*[@title="Download torrent"]').click()
        logger.debug(dl)
        logger.info('Torrent extracted from: %s', topic)
    except NoSuchElementException:
       logger.info("No new Download found in: %s", str(topic))

#Write the completed file
with open(fileCompleted, "w") as foCompleted:
    for i in reversed(completedsave):
        foCompleted.writelines(i + "\n")
foCompleted.close()

browser.quit()
logger.info("Browser closed.")
