from pathlib import Path
import requests
import os,sys
from qbclient import Client
from loguru import logger
import configparser

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver



#Variable Definition
topics = list()
topicstovisit = list()
completedsave = list()
completed = list()
fileCompleted = "completed.txt"

logger.add("720pdl.log", format="{time} - {level} - {message}")



#Write Configs
def cfgfile():
    if len(config.read('720pier.ru.ini')) == 0:  # if config file isn't found, create it
        cfgfile = open("720pier.ru.ini", 'w')
        config.add_section('Default')
        config.add_section('Credentials')
        config.add_section('Torrent')
        config.set('Default', 'savedir', str(Path.cwd()))
        config.set('Default', 'url', 'http://720pier.ru/search.php?search_id=active_topics&sr=topics&ot=1&pt=t&fid[]=46')
        config.set('Credentials', 'username', '<your 720pier.ru username>')
        config.set('Credentials', 'password', '<your 720pier.ru password>')
        config.set('Torrent', 'sendToQBittorrent', "no")
        config.set('Torrent', 'qbclient', 'http://127.0.0.1:8080')  # WEB-Access for qBittorrent must be available
        config.set('Torrent', 'category', '720pier')  # no category as standard
        config.set('Torrent', 'login', 'admin')  # Login to qBittorrent Client
        config.set('Torrent', 'password', 'admin')  # Password to qBittorrent Client
        config.set('Torrent', 'BasicAuthLogin', '')  # Basic Auth
        config.set('Torrent', 'BasicAuthPassword', '')  # Basic Auth
        config.set('Torrent', 'startPaused', 'yes')  # Start Downloads immediately (yes/no)

        config.write(cfgfile)
        cfgfile.close()

#Get Configs
config = configparser.ConfigParser()
cfgfile()
config.read('720pier.ru.ini')
cfgSaveDir=Path(config['Default']['savedir'])
cfgUsername=config['Credentials']['username']
cfgPassword=config['Credentials']['password']
cfgSendToQb=config['Torrent'].getboolean('sendToQBittorrent')
cfgQbClient=config['Torrent']['qbclient']
cfgQbCategory=config['Torrent']['category']
cfgQbUsername=config['Torrent']['login']
cfgQbPassword=config['Torrent']['password']
cfgBasicAuthLogin=config['Torrent']['BasicAuthLogin']
cfgBasicAuthPassword=config['Torrent']['BasicAuthPassword']
cfgQbDownload=config['Torrent']['startPaused']


def readFinishedCrawls():
    # Read already finished Crawls
    try:
        with open(fileCompleted, "r") as foCompleted:
            for line in foCompleted:
                completed.append(line.rstrip())
    except FileNotFoundError:
        open(fileCompleted, "x")

def scanForFiles():
    setOfFiles = set()
    currentDirectory = os.path.abspath(os.path.dirname(__file__))
    files = os.listdir(currentDirectory)
    for file in files:
        if file.endswith('.torrent'):
            setOfFiles.add(os.path.join(os.path.abspath(os.path.dirname(__file__)), file))
    return setOfFiles
    
def getNewTorrents():
    visited = bool
    if cfgUsername == "<your 720pier.ru username>":
        print("Please adapt 720pier.ru.ini to your needs")
        sys.exit(1)

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
    service = Service(log_path=os.path.devnull)
    #service = Service(log_path="")
    browser = WebDriver(service=service, options=options)
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
        #logger.debug(topic)
        for c in completed:
            if c==str(topic.get_attribute('href')):
                visited=True
                completedsave.append(c)
                logger.info(f"Topic has already been visited: {c}")
        if not visited:
            topicstovisit.append(topic.get_attribute('href'))
            completedsave.append(topic.get_attribute('href'))
            logger.info(f"Topic added to list: {topic.get_attribute('href')}")
        visited=False

    #Open Topics and download the torrent file
    for topic in topicstovisit:
        browser.get(topic)
        logger.info(f'Trying: {topic}')
        try:
            dl = browser.find_element(By.XPATH,'//*[@title="Download torrent"]').click()
            #logger.debug(dl)
            logger.info(f'Torrent extracted from: {topic}')
        except NoSuchElementException:
            logger.info(f"No new Download found in: {str(topic)}")

    #Write the completed file
    with open(fileCompleted, "w") as foCompleted:
        for i in reversed(completedsave):
            foCompleted.writelines(i + "\n")
    foCompleted.close()

    browser.quit()
    logger.info("Browser closed.")


if __name__ == "__main__":
    readFinishedCrawls()
    getNewTorrents()
    if cfgSendToQb == True:
        newFiles = scanForFiles()
        qb = Client(cfgQbClient, True, cfgBasicAuthLogin, cfgBasicAuthPassword)
        qb.login(cfgQbUsername, cfgQbPassword)
        newFiles = scanForFiles()
        for file in newFiles:
            buffer = open(file, "rb")
            buffered = buffer.read()
            try:
                qb.download_from_file(buffered, category=cfgQbCategory, paused=cfgQbDownload)
                logger.info(f"{file} sent to QBittorrent.")
                os.remove(file)
            except Exception as e:
                logger.error(e)
            buffer.close()