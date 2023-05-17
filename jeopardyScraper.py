import requests
from bs4 import BeautifulSoup
import re
import time
from tinydb import TinyDB, Query
from dateutil.parser import parse

db = TinyDB('clues_db.json')

def scrapeGame(url):
    game_source = requests.get(url).text
    game_soup = BeautifulSoup(game_source, 'html')

    var_question = ''
    var_answer = ''       
    var_category = ''
    cats = []

    game_date = parse(game_soup.find(id='game_title').get_text().split('-')[1])

    categories = game_soup.find_all(class_="category_name")
    for cat in categories:
        cats.append(cat.get_text())

    clues = game_soup.find_all(class_="clue")
    for n in range(0,len(clues)):
        c = clues[n]
        ct = c.find_all(class_="clue_text")
        
        try:
            cat_index = int(ct[0]['id'][-3]) - 1
        except ValueError:
            continue
        except TypeError:
            continue

        var_category = cats[cat_index]
        var_question = ct[0].contents[0].get_text()
        var_answer = ct[1].find(class_="correct_response").contents[0].get_text()

        if c.find(class_="clue_value") is not None:
            cv = c.find(class_="clue_value").get_text()
            var_value = cv
    
        QNA = {
                "month": game_date.month,
                "year": game_date.year,
                "category": var_category,
                "question": var_question,
                "answer": var_answer,
                "value": var_value
              }

        db.insert(QNA)

def scrapeSeason(url):
    season_source = requests.get(url).text
    season_soup = BeautifulSoup(season_source)
    games = []
    gameLinks = season_soup.find_all(href=re.compile("game_id"))

    for game in gameLinks:
        gameHref = game.get('href')
        gameId = gameHref[(gameHref.find('=')+1):]
        gameLink = 'https://www.j-archive.com/showgame.php?game_id={0}'.format(gameId)

        scrapeGame(gameLink)
        print(f'scraped game {gameId}')

        time.sleep(2)

def main():
    seasons_source = requests.get("https://www.j-archive.com/listseasons.php").text
    seasons_soup = BeautifulSoup(seasons_source)
    
    content = seasons_soup.find(id='content')
    seasons = content.find_all(href=re.compile("season"))

    for s in range(0,(len(seasons))):
        seasonurl = 'https://www.j-archive.com/' + seasons[s]['href']
        scrapeSeason(seasonurl)

if __name__ == "__main__":
    main()