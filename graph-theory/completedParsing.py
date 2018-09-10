
## All this does is parsing and create dictionaries.
## Dictionaries made:
## (1) Get gexf files to match Jermaine
## (2) Get year, genres, actors
## Pass dictionaries to pickle files.
## Pickle files are used for 
## rebuilding dictionaries in predict function.

import networkx as nx
import snap
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import urllib
import csv
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import numpy as np
import pickle
import enchant

def save_dictionary(current_dict, filename):
    with open(filename + '.pkl', 'wb') as f:
        pickle.dump(current_dict, f, pickle.HIGHEST_PROTOCOL)

## just scrolls throme the movie galaxies webpage
driver = webdriver.Chrome()
driver.get("http://moviegalaxies.com/movies")
i = 0
while i != 200:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.3)
    i += 1

page_source = driver.page_source
link_global = "http://moviegalaxies.com/movies"
soup = BeautifulSoup(page_source)
all_links = soup.find_all("a")
urls_list = []
for link in all_links:
    partial_link = link.get("href") # in the form /movies/250-The-Departed
    exploded_partial_list = partial_link.split("-")
    if len(exploded_partial_list) > 1:
        movie_url = urljoin(link_global, partial_link)
        if movie_url not in urls_list:
            urls_list.append(movie_url)
print len(urls_list) # should be 774

tags = {} # map test_url to list of tags
for test_url in urls_list:
    tags[test_url] = []

count = 0 # acts like progress bar
for test_url in urls_list:
    print count
    try:
        test_page = urllib2.urlopen(test_url)
        soup = BeautifulSoup(test_page)
        
        all_links = soup.find_all("a", href=lambda href: href and "index" in href)
        
        for link in all_links:
            partial_link = link.get("href")
            if partial_link != None:
                exploded_partial_link = partial_link.split("/")
                for current_string in exploded_partial_link:
                    if "tag" in current_string:
                        tag_exploded = current_string.split(":")   
                        actual_tag = tag_exploded[1]
                        tags[test_url].append(actual_tag)
        count += 1
    except:
        print test_url
        count += 1

new_tags = {}
d = enchant.Dict("en_US")
for key, value in tags.iteritems():
    genres = []
    for current_string in value:
        if d.check(current_string):
            genres.append(current_string) 
    new_tags[key] = genres


# make dictionaries
# num : movie name
# num : genres
# genre : movie indices
id_to_movie_name = {}
id_to_genres = {}
for current_url, genre_list in new_tags.iteritems():
    exploded_string = current_url.split('/')
    exploded_again_string = exploded_string[-1].split('-')
    
    try:
        movie_id = int(exploded_again_string[0])
    except:
        print current_url
        print exploded_again_string[0]
        continue
    movie_list = exploded_again_string[1:]
    movie_title = ' '.join(movie_list)
    
    id_to_movie_name[movie_id] = movie_title
    id_to_genres[movie_id] = genre_list

# genres to ids
genre_to_ids = {}
for movie_id, genre_list in id_to_genres.iteritems():
    for genre in genre_list:
        if genre not in genre_to_ids:
            genre_to_ids[genre] = []
        genre_to_ids[genre].append(movie_id)

# some genres are not valid
new_genre_to_ids = {}
for key, value in genre_to_ids.iteritems():
    if len(value) > 50: # only saves genres with more than 50 movies
        new_genre_to_ids[key] = value

# remake id_to_genres
new_id_to_genres = {}
for movie_id, genre_list in id_to_genres.iteritems():
    new_id_to_genres[movie_id] = [] # initialize to nothing
    
for movie_id, genre_list in id_to_genres.iteritems():
    for genre in genre_list:
        if genre in new_genre_to_ids.iterkeys():
            new_id_to_genres[movie_id].append(genre)

save_dictionary(new_id_to_genres, 'id_to_genres')
save_dictionary(new_genre_to_ids, 'genre_to_ids')
save_dictionary(id_to_movie_name, 'id_to_movie_name')




