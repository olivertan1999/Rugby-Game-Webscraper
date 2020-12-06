# Rugby-Game-Webscraper

# Introduction
The aim of this project is to crawl and scrape information from a number of rugyby game media reports and use that information to improve our understanding of team performance. The seed URL is http://comp20008-jh.eng.unimelb.edu.au:9889/main/.

# scraper.py
This script contains codes that
- Extract URL and headline of each article and compile them into a csv file named `task1.csv`.
- Visit each URL from `task1.csv` and extract the first named team along with the largest match score in the article. Then compile the URL, headline along with the relevant team names and match scores into a csv file named `task2.csv`. **Some articles may not contain a team name and/or a match score. These articles will be discarded.**
- Produce a csv file named `task3.csv` containing the team name and average game difference for each team in `task2.csv`. 
- Generate a plot (saved as `task4.png`) showing the five teams that articles are most frequently written about and the number of times an article is written about that team.
- Generate a plot (saved as `task5.png`) comparing the number of articles written about each team with their average game difference. 
# Analysis and Report
Refer to the [report](https://github.com/olivertan1999/Rugby-Game-Webscraper/blob/main/RugbyGameReport.pdf) for a detailed explanation of the result and limitations of the methods and algorithms used.
