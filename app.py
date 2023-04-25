from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from log_config import configure_logging
from bs4 import BeautifulSoup

import urllib.parse
import uuid
import time
import random
import requests
import json

import os
import logging

print('creating logs folder and configuring logging')
os.makedirs('logs', exist_ok=True)
configure_logging()
# configure logging for the selenium and bs4 modules to Exception to a crash at debug level
_level = logging.ERROR
selenium_logger = logging.getLogger('selenium')
selenium_logger.setLevel(_level)

bs4_logger = logging.getLogger('bs4')
bs4_logger.setLevel(_level)

logger = logging.getLogger()

logger.info('begginning application')


def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                # get the size of the file
                size = os.path.getsize(file_path)
                total_size += size
            except OSError:
                # ignore errors caused by files that cannot be accessed
                pass
    return total_size


def get_bay12_urls(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'unable to locate url file at {file_path}')
    urls = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('http://www.bay12forums.com/smf/index.php?topic='):
                urls.append(line)
    return urls







# specify the path to the chromedriver executable
chrome_driver_path = 'chromedriver.exe'

if not os.path.exists(chrome_driver_path):
    raise FileNotFoundError('unable to locate chromedriver.exe file. it must be in the same folder as this python script')
logger.info('loading driver')
try:
    logger.info('loading list of threads to scrape')
    base_urls = get_bay12_urls(os.path.join('data', 'url_list.txt'))

    url_conversions = []

    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    for base_url in base_urls:
        logger.info(f'begginning scraping of {base_url}')
        # encoded_url = urllib.parse.quote(base_url, safe=':/?&=')
        topic = str(urllib.parse.parse_qs(urllib.parse.urlparse(base_url).query)["topic"][0])

        # create list of posts
        posts = {}
        page_count = 0
        image_extensions = ['jpg', 'jpeg', 'png', 'gif']

        # navigate to the base thread url to get number of pages
        logger.info(f'navigating to {base_url}')
        try:
            driver.get(base_url)
        except TimeoutException as e:
            logger.error('timeout occured')
            driver = webdriver.Chrome(executable_path=chrome_driver_path)
            continue
        except WebDriverException as e:
            logger.exception(e, exc_info=True, stack_info=True)
            driver = webdriver.Chrome(executable_path=chrome_driver_path)
            continue

        # extract the HTML content of the page
        html_content = driver.page_source
        
        # create a BeautifulSoup object from the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # find last page
        navpages = soup.find_all('a', class_='navPages')
        last_navpage = navpages[-1]

        logger.info(f'last_navpage is {last_navpage.string}')

        try:
            last_page_num = int(last_navpage.string)
        except ValueError:
            logger.error(f'Failed to convert last navPage to integer "{last_navpage.string}" to int')

        # create the topic folder
        folder_path = os.path.join('data', 'topic', str(topic))
        os.makedirs(folder_path, exist_ok=True)

        post_number = 0
        for i in range(last_page_num):
            url = f"{base_url}.{page_count}"
            logger.info(f'navigating to page {i} of {last_page_num} at {url}')
            # navigate to the thread_url
            try:
                driver.get(base_url)
            except TimeoutException as e:
                logger.error('timeout occured')
                driver = webdriver.Chrome(executable_path=chrome_driver_path)
                continue
            except WebDriverException as e:
                logger.exception(e, exc_info=True, stack_info=True)
                driver = webdriver.Chrome(executable_path=chrome_driver_path)
                continue

            # wait for a div with class="post" to be present
            wait = WebDriverWait(driver, 30, poll_frequency=1)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.post')))
            time.sleep(5)

            # extract the HTML content of the page
            html_content = driver.page_source

            # create a BeautifulSoup object from the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')            

            # get the forumposts div
            forum_posts_div = soup.find('div', {'id': 'forumposts'})
            
            # create a BeautifulSoup object from just the forum posts
            forum_posts_soup = BeautifulSoup(str(forum_posts_div), 'html.parser') 

            # soup = BeautifulSoup(forum_posts_div.)
            # extract the text from each post div
            for div in forum_posts_soup.find_all('div', class_='bordercolor'):
                post_number += 1

                logger.info(f'reading post {post_number}')
                
                post_soup = BeautifulSoup(str(div), 'html.parser') 
                # get the username
                post_username = post_soup.find('a', href=True, title=lambda value: value and 'View the profile of' in value).text
                print(post_number, post_username)
                
                # get the post text
                post_text = post_soup.find('div', class_='post')
                # print(post_text)

                # add the post content to the dictionary
                posts[post_number] = (post_username, post_text)

                # find all img elements in the post
                img_tags = post_soup.find_all('img')
                
                # create a folder hierarchy to save the images
                if len(img_tags) > 0:
                    logger.info(f'found {len(img_tags)} images in post...')
                    folder_path = os.path.join('data', 'topic', topic, f'post_{str(post_number)}')
                    os.makedirs(folder_path, exist_ok=True)
                
                # extract the src attribute of each img element that has a valid image file extension
                img_tag_count = 0
                for img_tag in img_tags:
                    img_tag_count += 1
                    #sleep a random time to prevent rate limiting
                    _sleeptime = max(1, float(random.normalvariate(3, 2)))
                    # logger.info(f'sleeping for {_sleeptime} to avoid rate limiting')
                    time.sleep(_sleeptime)
                    # download the image   
                    src = img_tag.get('src')
                    if src and any(src.lower().endswith(ext) for ext in image_extensions):
                        # create a unique identifier for each image
                        image_id = str(uuid.uuid4())
                        logger.info(f'pulling image {img_tag_count} of {len(img_tags)} at {src}')
                        try:
                            driver.get(base_url)
                        except TimeoutException as e:
                            logger.error('timeout occured')
                            driver = webdriver.Chrome(executable_path=chrome_driver_path)
                            continue
                        except WebDriverException as e:
                            logger.exception(e, exc_info=True, stack_info=True)
                            driver = webdriver.Chrome(executable_path=chrome_driver_path)
                            continue
                        if "captcha" in driver.current_url.lower() or "captcha" in driver.page_source:
                            logger.warning(f"CAPTCHA detected. skipping. url is {src}")
                            continue
                        _filepath = os.path.join('data', 'topic', topic, f'post_{str(post_number)}', os.path.basename(src))
                        logger.debug(f'writing file {_filepath}')
                        try:
                            response = requests.get(src)
                        except (requests.exceptions.RequestException, ConnectionError) as e:
                            logger.exception(e, stack_info=True)
                            continue

                        if os.path.exists(_filepath):
                            logging.warning(f'{_filepath} already exists, overwriting...')
                            _filepath = _filepath + "_1"
                        with open(_filepath, 'wb') as f:
                            f.write(response.content)
                        # log the url change
                        url_conversions.append((src, _filepath))
                                            
            # increment by 15 because bay12 is weird like that
            page_count += 15

except SessionNotCreatedException as e:
    logger.exception(f'unable to create session. please verify that your webdriver version matches the installed chrome version, {e}')
except NoSuchWindowException as e:
    logger.exception('application closed because the selenium window was activily closed')
except KeyboardInterrupt:
    logger.exception('application closed at request of user (ctrl + c)')
except WebDriverException as e:
    pass
except Exception as e:
    logger.critical('an unknown exception has occured. please send the app.log and url_list.txt files to https://github.com/Celebrinborn/Bay12_Imgur_Archive', exc_info=True, stack_info=True)
    logger.critical(e)
    raise e
finally:
    logger.info('writing posts info')
    with open(os.path.join('data', 'topic', str(topic), 'thread.html'), 'w', encoding='utf-8') as f:
        # sort the dictionary keys in ascending order
        sorted_keys = sorted(posts.keys())
        # loop through the sorted keys
        for key in sorted_keys:
            # get the username and text for the current post
            username, text = posts[key]
            # write the post number, username, and text to the file with a horizontal line between them
            f.write(f'{key} | by {username}:\n')
            f.write(f'{text}\n')
            f.write('-' * 80)
            f.write('\n')
    logger.info('writing conversations.json')
    with open(os.path.join('data', 'url_conversions.json'), 'w', encoding='utf-8') as f:
        # serialize the list as JSON and write it to the file
        json.dump(url_conversions, f)

