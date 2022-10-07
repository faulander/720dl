from pathlib import Path
import os
import sys
from loguru import logger
import pendulum
import feedparser
import yaml
import schedule
import time
from yaml.loader import BaseLoader
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver

from qbclient import Client


def loadOrCreateCfgfile():
    if os.path.isfile('720pier.ini.yml'):
        with open('720pier.ini.yml', "r") as ini:
            c = yaml.load(ini, Loader=BaseLoader)
            #logger.debug(c)
        return c
        logger.info("INI File loaded")
    else:
        c = dict()
        c['Default'] = dict()
        c['Default']['savedir'] = str(Path.cwd())
        c['Default']['baseURL'] = 'https://720pier.ru'
        c['Default']['useRSS'] = False
        c['Default']['categoriesToDownload'] = [48,]
        c['Default']['skipOlderThan'] = today.start_of("year").format("YYYY-MM-DD")
        c['Default']['include'] = ['',]
        c['Default']['exclude'] = ['',]
        c['Credentials'] = dict()
        c['Credentials']['username'] = '<your 720pier.ru username>'
        c['Credentials']['password'] = '<your 720pier.ru password>'
        c['Torrent'] = dict()
        c['Torrent']['sendToQBittorrent'] = False
        c['Torrent']['qbClient'] = 'http://127.0.0.1:8080' # WEB-Access for qBittorrent must be available
        c['Torrent']['category'] = '720pier'  # 
        c['Torrent']['qbUsername'] = 'admin'  # Login to qBittorrent Client
        c['Torrent']['qbPassword'] = 'admin'  # Password to qBittorrent Client
        c['Torrent']['basicAuthUsername'] = ''  # Basic Auth
        c['Torrent']['basicAuthPassword'] = '' # Basic Auth
        c['Torrent']['startPaused'] = True  # Start Downloads immediately (yes/no)
        with open('720pier.ini.yml', "w") as ini:
            yaml.dump(c, ini, default_flow_style=False, sort_keys=False)
        logger.error('Default config file created. Please adapt!')
        sys.exit(1)

def readFinishedCrawls():
    # Read already finished Crawls
    try:
        with open(fileCompleted, "r") as foCompleted:
            for line in foCompleted:
                completed.append(line.rstrip())
        return completed
    except FileNotFoundError:
        open(fileCompleted, "x")
    logger.info("Completed file loaded")

def scanForFiles():
    setOfFiles = set()
    currentDirectory = os.path.abspath(os.path.dirname(__file__))
    files = os.listdir(currentDirectory)
    for file in files:
        if file.endswith('.torrent'):
            setOfFiles.add(os.path.join(os.path.abspath(os.path.dirname(__file__)), file))
    return setOfFiles
    logger.info("Scan for torrent files locally completed")
    
def getNewTorrents():
    visited = bool
    if cfg['Credentials']["username"] == "<your 720pier.ru username>":
        logger.error("Please adapt 720pier.ini.yml to your needs")
        sys.exit(1)

    # Set Firefox Environmental Variables
    options = Options()
    options.set_preference("browser.download.dir", os.path.abspath(os.path.dirname(__file__)))
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
    browser = WebDriver(service=service, options=options)
    logger.info("Firefox Preferences set.")

    #Login to the page
    try:
        login = cfg['Default']['baseURL'] + "/ucp.php?mode=login"
        browser.get(login)
        assert '720pier' in browser.title
        logger.info("Loginpage opened.")
        elem = browser.find_element(By.ID,'username')
        elem.send_keys(cfg['Credentials']["username"])
        elem = browser.find_element(By.ID,'password')
        elem.send_keys(cfg['Credentials']["password"])
        elem = browser.find_element(By.NAME,'login').click()
    except Exception as e:
        if hasattr(e, 'message'):
            logger.error(e.message)
        else:
            logger.error(e)
        sys.exit(1)

    browser.implicitly_wait(0.5)

    #Find all Topics and their Links
    topics = list()
    if cfg['Default']["useRSS"] == "false":
        for cat in cfg['Default']['categoriesToDownload']:
            url = cfg['Default']['baseURL'] + '/viewforum.php?f='
            url = url + cat
            logger.info(f'Trying category {cat}')
            try:
                browser.get(url)
                browser.implicitly_wait(3)
            except Exception as e:
                if hasattr(e, 'message'):
                    logger.error(e.message)
                else:
                    logger.error(e)
                sys.exit(1)
            topics = browser.find_elements(By.CLASS_NAME,'topictitle')
            for topic in topics:
                #timeOfPost = browser.find_element_by_xpath("//time").get_attribute("datetime")
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
    else:
        includedList = cfg['Default']["include"]
        excludedList = cfg['Default']["exclude"]
        baseFeedURL = "https://720pier.ru/feed/forum/"
        for category in cfg['Default']["categoriesToDownload"]:
            feed = feedparser.parse(baseFeedURL + str(category))
            for entry in feed.entries:
                isIncluded = False
                isExcluded = False
                if pendulum.parse(cfg['Default']["skipOlderThan"]) <= pendulum.parse(entry.published):
                    if len(cfg['Default']["include"]) > 0:
                        for inc in includedList:
                            if entry.title.find(inc) >= 0:
                                isIncluded = True
                                logger.info(f"Included '{inc}' has been found in Title: '{entry.title}'")
                            if entry.description.find(inc) >=0:
                                logger.info(f"Included '{inc}' has been found in Description: '{entry.description}'")
                                isIncluded = True
                    else:
                        isIncluded = True
                    if len(cfg['Default']["exclude"]) > 0:
                        for exc in includedList:
                            if entry.title.find(exc) >= 0:
                                isExcluded = True
                                logger.info(f"Excluded '{exc}' has been found in Title: '{entry.title}'")
                            if entry.description.find(exc) >=0:
                                logger.info(f"Excluded '{exc}' has been found in Description: '{entry.description}'")
                                isExcluded = True
                    else:
                        isExcluded = False
                    if isIncluded and not isExcluded:
                        topics.append(entry.link)
                else:
                    logger.info("RSS Entry is too old.")
        for topic in topics:
            for c in completed:
                if c == topic:
                    visited=True
                    completedsave.append(c)
                    logger.info(f"Topic has already been visited: {c}")
            if not visited:
                topicstovisit.append(topic)
                completedsave.append(topic)
                logger.info(f"Topic added to list: {topic}")
            visited=False

    #Open Topics and download the torrent file
    for topic in topicstovisit:
        browser.get(topic)
        logger.info(f'Trying: {topic}')
        if len(cfg['Default']['skipOlderThan']) > 0:
            postingDeadline = pendulum.parse(cfg['Default']['skipOlderThan'])
            timeOfPost = pendulum.parse(browser.find_element(By.TAG_NAME, "time").get_attribute('Datetime'))
            if timeOfPost >= postingDeadline:
                try:
                    dl = browser.find_element(By.XPATH,'//*[@title="Download torrent"]').click()
                    logger.info(f'Torrent extracted from: {topic}')
                except NoSuchElementException:
                    logger.info(f"No new Download found in: {str(topic)}")
            else:
                logger.error('Posting is too old.')
        else:
            try:
                dl = browser.find_element(By.XPATH,'//*[@title="Download torrent"]').click()
                logger.info(f'Torrent extracted from: {topic}')
            except NoSuchElementException:
                logger.info(f"No new Download found in: {str(topic)}")


    #Write completed file
    with open(fileCompleted, "w") as foCompleted:
        for i in reversed(completedsave):
            foCompleted.writelines(i + "\n")
    foCompleted.close()

    browser.quit()
    logger.info("Browser closed.")

def sendFilesToQb():
    newFiles = scanForFiles()
    qb = Client(cfg["Torrent"]["qbClient"], True, cfg["Torrent"]["basicAuthUsername"], cfg["Torrent"]["basicAuthPassword"])
    qb.login(cfg["Torrent"]["qbUsername"], cfg["Torrent"]["qbPassword"])
    newFiles = scanForFiles()
    for file in newFiles:
        buffer = open(file, "rb")
        buffered = buffer.read()
        try:
            qb.download_from_file(buffered, category=cfg["Torrent"]["category"], paused=cfg["startPaused"])
            logger.info(f"{file} sent to QBittorrent.")
            os.remove(file)
        except Exception as e:
            logger.error(e)
        buffer.close()
    qb.logout()

def main():
    getNewTorrents()
    if cfg["Torrent"]["sendToQBittorrent"] == "true":
        sendFilesToQb()
    completed = readFinishedCrawls()


#Variable Definition
topics = list()
topicstovisit = list()
completedsave = list()
completed = list()
fileCompleted = "completed.txt"
today = pendulum.now()
cfg = dict()

logger.add("720pdl.log", format="{time} - {level} - {message}")

cfg = loadOrCreateCfgfile()
completed = readFinishedCrawls()

#schedule.every(5).minutes.do(main)

#while True:
#    schedule.run_pending()
#    time.sleep(1)

main()