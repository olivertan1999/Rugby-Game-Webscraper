# Element of Data Processing Assignment 1
# Student Name: Ming Hui Tan 

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import unicodedata
import re
import matplotlib.pyplot as plt
import seaborn as sns
from numpy import arange

# TASK 1 (Webcrawling)
# Specify the initial page to crawl
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'

seed_url = base_url
page = requests.get(seed_url)
soup = BeautifulSoup(page.text, 'html.parser')

visited = {}; 
visited[seed_url] = True
data = {'Headline':[],'URL':[]}
pages_visited = 1


links = soup.findAll('a')

to_visit_relative = [l for l in links]

# Resolve to absolute urls
to_visit = []
for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))

    
# Find all outbound links on succsesor pages and explore each one 
while (to_visit):
    # consume the list of urls
    link = to_visit.pop(0)
    data['URL'].append(link)
    
    # need to concat with base_url, an example item <a href="catalogue/sharp-objects_997/index.html">
    page = requests.get(link)
    
    # scraping code goes here
    soup = BeautifulSoup(page.text, 'html.parser')
    headline = soup.findAll('h1')
    data['Headline'].append(headline[0].text.strip())
    
    # mark the item as visited, i.e., add to visited list, remove from to_visit
    visited[link] = True
    to_visit
    new_links = soup.findAll('a')
    for new_link in new_links :
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)


data = pd.DataFrame(data)

# Save the file as csv 
data.set_index('Headline', inplace = True)
data.to_csv('task1.csv')

#TASK 2 (Webscraping)
import json
import nltk

# Find the names of teams
with open('rugby.json') as f:
    rugby_data = json.load(f)
    rugby_teams = []
    for team in rugby_data['teams']:
        rugby_teams.append(team['name'])

# Function to find the largest score in the article and return the index
# of the largest score in the score_list
def largest_score(score_list):
    # Define a weightage for each score
    score_weight = 0.5
    
    largest_weighted_score = 0
    largest_score_idx = None
    
    for score_idx in range(len(score_list)):
        first_score = re.search(r'(\d+)-', score_list[score_idx]).group(1)
        second_score = re.search(r'-(\d+)', score_list[score_idx]).group(1)
        weighted_score = score_weight * int(first_score) + (1 - score_weight) * int(second_score)
        # Largest possible match score is 145-17 
        if (weighted_score > largest_weighted_score) and (int(first_score) < 400 and int(second_score) < 400):
            largest_weighted_score = weighted_score
            largest_score_idx = score_idx
            
    return largest_score_idx

new_data = {'Headline':[],'URL':[], 'Team':[], 'Score':[]}
team_count = 0
score_count = 0

# Visit and scrape information from each URL
for url in data['URL']:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    headline = soup.find(id = 'headline').get_text()
    section = soup.find(id = 'article_detail')
    article = section.get_text()
    content = " ".join([headline, article])
    main_team = None
    
    # Regular expression to find names of team in the article
    search_list_re = re.compile(r'\b(%s)\b'%'|'.join(rugby_teams))
    teams_mentioned = re.findall(search_list_re, content)
    
    # If the article does not have any team mentioned, skip and visit the next article
    if not teams_mentioned:
        continue
    
    main_team = teams_mentioned[0]
    
    # Match and find all scores in the article with regex
    scores = [score for score in re.findall(r'\d+\-\d+', content)]
    
    # If no score, skip and visit the next URL
    if not scores:
        continue
    
    # Find the largest score
    largest_score_idx = largest_score(scores)
    
    # If no largest score, skip and visit the next URL
    if largest_score_idx == None:
        continue
    
    new_data['Headline'].append(headline)
    new_data['URL'].append(url)
    new_data['Team'].append(main_team)
    new_data['Score'].append(scores[largest_score_idx])
    
# Create a dataframe for all the relevant information from the webscraping    
new_dataframe = pd.DataFrame(new_data)
new_dataframe.set_index('Headline', inplace = True)
new_dataframe.to_csv('task2.csv')

# TASK 3 (Finding Average Game Difference)

# Split the original match score into score 1 and score 2 then calculate the 
# Absolute difference between them
new_dataframe['Score1'] = new_dataframe['Score'].str.extract(r'(\d+)\-').astype(int)
new_dataframe['Score2'] = new_dataframe['Score'].str.extract(r'\-(\d+)').astype(int)
new_dataframe['AbsoluteGameDifference'] = abs(new_dataframe['Score1'] - new_dataframe['Score2'])

# Find the average game difference of each team
avg_game_diff = new_dataframe[['Team','AbsoluteGameDifference']].groupby(['Team']).mean()
avg_game_diff.rename(columns = {'AbsoluteGameDifference':'avg_game_difference'}, inplace = True)
avg_game_diff.to_csv('task3.csv')

# TASK 4 (Plot Top 5 Most Written About Teams)

# Group and count number of appearance of each team in the data
team_article_data = new_dataframe.groupby('Team')['Team'].count().sort_values(ascending = False)
team_article_data = pd.DataFrame(team_article_data)
team_article_data.rename(columns = {'Team':'Count'}, inplace = True)
team_article_data.reset_index(inplace = True)

# Plot the information in a graph
plt.figure(figsize = (8,6)) 

team_count_plot = sns.barplot(data = team_article_data[:5], x = 'Team', y = 'Count')
sns.set_context('notebook',font_scale = 1.2) 
plt.xticks(horizontalalignment = 'center',
           fontweight = 'light',
           fontsize = 15.0)
plt.yticks(fontsize = 15.0)
plt.ylim(0, 22)
plt.xlabel('Team', fontsize = 15.0)
plt.ylabel('Number of articles written about the team', fontsize = 15.0)
plt.title('Top 5 Teams That Articles Are Most Frequently Written About', y=1.02)
plt.savefig('task4.png')

# TASK 5 (Plot number of articles written about each team against their average game difference)

# Find the number of appearance of all teams in the data
full_team_data = new_dataframe.groupby('Team')['Team'].count().sort_values(ascending = False)
full_team_data = pd.DataFrame(full_team_data)
full_team_data.rename(columns = {'Team':'Count'}, inplace = True)

# Join this information with the average game difference table in TASK 3
join_data = full_team_data.join(avg_game_diff)
join_data.reset_index(inplace = True)
my_range = range(1, len(join_data.index) + 1)

# Plot this information in a double bar plot
plt.figure(figsize = (10,6)) 
plt.bar(arange(len(join_data['avg_game_difference']))-0.12, join_data['avg_game_difference'], width=0.25)
plt.bar(arange(len(join_data['Count']))+0.13,join_data['Count'], width=0.25, color='r')
plt.xticks(arange(len(join_data['Team'])),join_data['Team'])
plt.legend(['Average game difference','Number of articles written about them'], fontsize = 15.0)

plt.xticks(horizontalalignment = 'center',
           fontweight = 'light',
           fontsize = 15.0)
plt.yticks(fontsize = 15.0)
plt.title('Comparison between the number of articles written about \n each team with their average game difference', y=1.02, fontsize = 15.0)
plt.tight_layout()
plt.savefig('task5.png')

# EXTRA (Find the correlation in join_data)
# join_data.corr()
