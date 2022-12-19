from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import glob
import pandas as pd
import datetime
import sys
import os
import os.path
import time
import csv

def user_agent():
    user_agent_list = []
    with open('user_agents.csv', 'r') as f:
        for agents in f:
            user_agent_list.append(agents)
    return user_agent_list

def convert_row( row ):
    row_dict = {}
    for key, value in row.items():
        keyAscii = key.encode('ascii', 'ignore' ).decode()
        valueAscii = value.encode('ascii','ignore').decode()
        row_dict[ keyAscii ] = valueAscii
    return row_dict

def scrape():
  time_start = datetime.datetime.now().replace(microsecond=0)
  directory = os.path.dirname(os.path.realpath(__file__))

  user_agents = user_agent()

  # Setup random proxy and user-agent
  random_user_agents = random.randint(1, len(user_agents) - 1)
  print(user_agents[random_user_agents])
  options = {
      'user-agent': user_agents[random_user_agents],
      'suppress_connection_errors': True,
      'verify_ssl': True
  }

  options = {
      'user-agent': user_agents[random_user_agents]
      # 'suppress_connection_errors': True
  }

  driver_path = os.path.join(directory, glob.glob('./chromedriver*')[0])
  browser = webdriver.Chrome(executable_path=driver_path, seleniumwire_options=options)

  browser.set_window_size(1920, 1080)

  title = []
  description = []
  thumbnail = []
  videoPublishedAt = []
  videoOwnerTitle = []
  videoOwnerChannelId = []
  videoId = []
  videoUrl = []
  viewCount = []
  likeCount = []
  videoCommentCount = []
  videoDuration = []

  with open('playlist.csv', encoding='unicode_escape') as f:

    reader = csv.DictReader(f)

    for line in reader:
      
      converted_row = convert_row( line )
      playlisturl = converted_row['playlisturl']

      browser.get(playlisturl)

      playlist_area = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, 'secondary')))

      items = playlist_area.find_elements(By.ID, "wc-endpoint")
      items_href = [item.get_attribute('href') for item in items]

      for href in items_href:
        
        try:
            browser.get(href)

            title_text = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="title"]/h1/yt-formatted-string'))).text
            title.append(title_text)

            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="description-inner"]'))).click()
            
            desc_text = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="description-inline-expander"]'))).text
            description.append(desc_text)

            vidId = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="below"]/ytd-watch-metadata'))).get_attribute('video-id')
            videoId.append(vidId)

            vidPublished = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="info"]/span[3]'))).text
            videoPublishedAt.append(vidPublished)
            print(f'{vidPublished}\n')

            vidOwner = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="text"]/a'))).text
            videoOwnerTitle.append(vidOwner)

            try:
                vidChannel = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ytp-ce-link'))).get_attribute('href')
            except:
                try:
                    vidChannel = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="watch7-content"]/meta[4]'))).get_attribute('content')
                except:
                    vidChannel = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="watch7-content"]/meta[5]'))).get_attribute('content')

            videoOwnerChannelId.append(vidChannel)

            vidViewCount = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="info"]/span[1]'))).text
            viewCount.append(vidViewCount)

            vidLikeCount = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button/div[2]/span'))).text
            likeCount.append(vidLikeCount)

            # vidCommentCount = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#count > yt-formatted-string > span:nth-child(1)'))).text
            # videoCommentCount.append(vidCommentCount)

            vidDuration = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ytp-time-duration'))).text
            videoDuration.append(vidDuration)

            vidThumb = "https://i.ytimg.com/vi/" + vidId + "/hqdefault.jpg"
            thumbnail.append(vidThumb)

            vidURL = "https://www.youtube.com/watch?v=" + vidId
            videoUrl.append(vidURL)

            print(f'{title_text}\n')

        except:
            pass
      

  time_end = datetime.datetime.now().replace(microsecond=0)
  runtime = time_end - time_start
  print(f"Script runtime: {runtime}.\n")

  # Save scraped URLs to a CSV file
  now = datetime.datetime.now().strftime('%Y%m%d-%Hh%M')
  print('Saving to a CSV file...\n')
  # print(f'URL: {len(url_list)}, City: {len(city_list)}, Prompt: {len(prompt_list)}, Composed: {len(composed_list)}\n')
  data = {"title": title, "description": description, "videoId": videoId, "videoPublishedAt": videoPublishedAt, "videoOwnerTitle": videoOwnerTitle, "videoOwnerChannelId": videoOwnerChannelId, "viewCount": viewCount, "likeCount": likeCount, "videoCommentCount": videoCommentCount, "videoDuration": videoDuration, "thumbnail": thumbnail, "videoUrl": videoUrl}
  df = pd.DataFrame.from_dict(data, orient='index')
  # df.index+=1
  df = df.transpose()

  filename = f"youtubePlaylistData{ now }.csv"

  print(f'{filename} saved sucessfully.\n')

  file_path = os.path.join(directory,'csvfiles/', filename)
  df.to_csv(file_path)

  browser.quit()

  time_end = datetime.datetime.now().replace(microsecond=0)
  runtime = time_end - time_start
  print(f"Script runtime: {runtime}.\n")

if __name__ == '__main__':
    scrape()