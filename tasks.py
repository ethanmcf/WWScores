from tracker import Score,db
from bs4 import BeautifulSoup
import time,re,requests,datetime
from datetime import date
from selenium import webdriver

HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"}
OHL_NAME_SWITCH = {
    'BAR':'Barrie Colts', 
    'ER':'Erie Otters', 
    'FLNT':'Flint Firebirds', 
    'GUE':'Guelph Storm', 
    'HAM':'Hamilton Bulldogs', 
    'KGN':'Kingston Frontenacs', 
    'KIT':'Kitchener Rangers', 
    'LDN':'London Knights', 
    'MISS':'Mississauga Steelheads', 
    'NIAG':'Niagara IceDogs', 
    'NB':'North Bay Battalion', 
    'OSH':'Oshawa Generals', 
    'OTT':'Ottawa 67s', 
    'OS':'Owen Sound Attack', 
    'PBO':'Peterborough Petes', 
    'SAG':'Saginaw Spirit', 
    'SAR':'Sarnia Sting', 
    'SSM':'Soo Greyhounds', 
    'SBY':'Sudbury Wolves', 
    'WSR':'Windsor Spitfires'
    } 
all_scores = []
all_links = []

def NHLScores(date):
    #url = "https://www.nhl.com/scores/2020-03-07"
    global all_scores,all_links
    url = "https://www.nhl.com/scores/"+str(date) 
    option = webdriver. ChromeOptions()
    option. add_argument('headless')
    browser = webdriver.Chrome('chrome_headless/chromedriver',options=option)
    browser.get(url)
    time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    #Gets the correct number of games for bs4 to process
    count = 0
    for z in re.finditer('nhl-scores__list-item nhl-scores__list-item--label',html):
        count+=1
        if count == 2:
            number_break = z.start()
    amount = 0
    for m in re.finditer('nhl-scores__list-item nhl-scores__list-item--game',html):
        if m.start() < number_break:
            amount += 1

    start_link = []
    for k in re.finditer('g5-component--nhl-scores__button g5-component--nhl-scores__button--box',html):
        start_link.append(k.start()-9)
    for n in range(amount):
        all_links.append("https://www.nhl.com/" + html[start_link[n]-34:start_link[n]])

    all_links.append('|')
    #Parses Html to get name and score
    team_name = soup.find_all('span',{'class':'g5-component--nhl-scores__team-name'})
    team_score = soup.find_all('span',{'class':'g5-component--nhl-scores__team-score'})

    #Adds team and cor. score to dict
    game_lst = []
    team_lst = []
    counter_2 = 0
    for i in range(amount*2):
        counter_2 += 1
        name = team_name[i].get_text().strip().replace(' ','!')
        score = team_score[i].get_text().strip()
        team = name + "!:!" + score
        team_lst.append(team)
        all_scores.append(team)
        if counter_2 == 2:
            game_lst.append(team_lst)
            team_lst=[]
            counter_2 = 0
    browser.quit()
    all_scores.append('|')

def USHLScores(date):
    #url = "https://www.ushl.com/view#/daily-schedule/2019-3-9?league=1&season=76&division=-1"
    global all_scores,all_links
    
    year = str(date.split("-")[0])
    month = str(date.split("-")[1]).replace("0","")
    day = str(date.split("-")[2]).replace("0","")
    d = year+"-"+month+"-"+day
    url = "https://www.ushl.com/view#/daily-schedule/"+d+"?league=1&season=76&division=-1"
    option = webdriver. ChromeOptions()
    option. add_argument('headless')
    browser = webdriver.Chrome('chrome_headless/chromedriver',options=option)
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    team_name = soup.find_all('div',{'class':'ht-team-name ng-scope'})
    team_score = soup.find_all('span',{'class':'ht-period-value ht-total ng-binding'})

    box = soup.find_all('a',{'class':'ht-sch-btn ng-scope'})

    for l in range(int(len(box)/2)):
        all_links.append('https://www.ushl.com/view' + box[l]['href'])

    all_links.append('|')

    game_lst = []
    team_lst = []
    counter_2 = 0
    for i in range(int(len(team_name)/2)):
        counter_2 += 1
        name = team_name[i].get_text().split("(")[0].replace("\n","").replace(' ','!')
        score = team_score[i].get_text().strip()
        team = name + "!:!" + score
        team_lst.append(team)
        all_scores.append(team)
        if counter_2 == 2:
            game_lst.append(team_lst)
            team_lst=[]
            counter_2 = 0
    browser.quit()
    all_scores.append('|')

def OHLScores(date):
    #url = "https://ontariohockeyleague.com/scores/2016-02-04"
    global all_scores,all_links,OHL_NAME_SWITCH
    
    url = "https://ontariohockeyleague.com/scores/" + date
    option = webdriver. ChromeOptions()
    option. add_argument('headless')
    browser = webdriver.Chrome('chrome_headless/chromedriver',options=option)
    browser.get(url)
    time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    team_name = soup.find_all('a',{'class':'table__link full-scores-game-content__team-link'})
    team_score = soup.find_all('td',{'class':'table__td full-scores-game-content__total'})

    box = soup.find_all('a',{'class':'full-scores-game__link'})
    count = 0
    for l in range(len(box)):
        count += 1
        if count == 2:
            all_links.append('https://ontariohockeyleague.com' + box[l]['href'])
            count = 0
    all_links.append('|')

    game_lst = []
    team_lst = []
    counter_2 = 0
    for i in range(int(len(team_name))):
        counter_2 += 1
        name = OHL_NAME_SWITCH[team_name[i].text.strip()].replace(' ','!')
        score = team_score[i].text.strip()
        team = name + "!:!" + score
        team_lst.append(team)
        all_scores.append(team)
        if counter_2 == 2:
            game_lst.append(team_lst)
            team_lst=[]
            counter_2 = 0
    browser.quit()

    all_scores.append('|')

def NCAAScores(date):
    #url = "https://www.ncaa.com/scoreboard/icehockey-men/d1/2021/04/08/all-conf"
    global all_scores,all_links,HEADERS
    
    year = str(date.split("-")[0])
    month = str(date.split("-")[1])
    day = str(date.split("-")[2])
    url = "https://www.ncaa.com/scoreboard/icehockey-men/d1/"+year+"/"+month+"/"+day+"/all-conf"
    html = requests.get(url,headers=HEADERS).content
    soup = BeautifulSoup(html, 'html.parser')
    team_name = soup.find_all('span',{'class':'gamePod-game-team-name'})
    team_score = soup.find_all('span',{'class':'gamePod-game-team-score'})

    box = soup.find_all('a',{'class':'gamePod-link'})
    for link in range(len(box)):
        all_links.append("https://www.ncaa.com" + box[link]['href'])
    all_links.append('|')

    game_lst = []
    team_lst = []
    counter_2 = 0
    for i in range(int(len(team_name))):
        counter_2 += 1
        name = team_name[i].get_text().strip().replace(' ','!')
        score = team_score[i].get_text().strip()
        team = name + "!:!" + score
        all_scores.append(team)
        if counter_2 == 2:
            game_lst.append(team_lst)
            team_lst=[]
            counter_2 = 0

    all_scores.append('|')

def OJHLScores(date):
    global all_scores,all_links,HEADERS
    
    year = str(date.split("-")[0])
    month = str(date.split("-")[1])
    day = str(date.split("-")[2])
    url = "http://ojhl_stats.wttstats.pointstreak.com/scoreboard.html?leagueid=231&seasonid=20521&month="+month+"&year="+year+"&date="+month+"/"+day+"/"+year[2:]
    team = ''
    html = requests.get(url,headers=HEADERS).content
    soup = BeautifulSoup(html, 'html.parser')

    team_name = soup.find_all('span',{'class':'nova-scoreboard__name'})
    team_score = soup.find_all('div',{'class':'nova-scoreboard__score'})

    divs = soup.find_all('li',{'class':'nova-links-list__item nova-links-list__item--btn'})
    for i in range(len(divs)):
        for j in range(int(len(divs)/4)):
            if i-(4*j) == 1:
                all_links.append("http://ojhl_stats.wttstats.pointstreak.com/" + divs[i].find('a')['href'])
    
    all_links.append('|')

    game_lst = []
    team_lst = []
    counter_2 = 0
    for i in range(int(len(team_name))):
        counter_2 += 1
        name = team_name[i].get_text().strip().replace(' ','!')
        score = team_score[i].get_text().strip()
        team = name + "!:!" + score
        all_scores.append(team)
        if counter_2 == 2:
            game_lst.append(team_lst)
            team_lst=[]
            counter_2 = 0

    all_scores.append('|')

def AHLScores(date):
    #url = "https://theahl.com/stats/daily-schedule/2021-3-27?league=4&season=68&division=-1"
    global all_scores,all_links
    
    year = str(date.split("-")[0])
    month = str(date.split("-")[1]).replace("0","")
    day = str(date.split("-")[2]).replace("0","")
    d = year+"-"+month+"-"+day
    url = "https://theahl.com/stats/daily-schedule/"+d+"?league=4&season=68&division=-1"
    option = webdriver. ChromeOptions()
    option. add_argument('headless')
    browser = webdriver.Chrome('chrome_headless/chromedriver',options=option)
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    box = soup.find_all('a',{'class':'ht-sch-btn'})

    for l in range(int(len(box)/2)):
        if l %3 == 0:
            all_links.append('https://theahl.com' + box[l]['href'])
    all_links.append('|')
    team_name = browser.find_elements_by_css_selector('div.ht-team-name')
    team_score = browser.find_elements_by_css_selector('span.ht-total.ht-period-value')

    counter_2 = 0
    for i in range(int(len(team_name)/2)):
        counter_2 += 1
        name = team_name[i].text.split("\n")[0].strip().replace(' ','!')
        score = team_score[i].text.strip()
        team = name + "!:!" + score
        all_scores.append(team)
    browser.quit()

    all_scores.append('|')

def BCHLScores(date):
    #url = "https://bchl.ca/stats/daily-schedule/2020-2-29?league=1&season=42&division=-1"
    global all_scores,all_links
    
    year = str(date.split("-")[0])
    month = str(date.split("-")[1]).replace("0","")
    day = str(date.split("-")[2]).replace("0","")
    d = year+"-"+month+"-"+day
    url = "https://bchl.ca/stats/daily-schedule/"+d+"?league=1&season=42&division=-1"
    option = webdriver. ChromeOptions()
    option. add_argument('headless')
    browser = webdriver.Chrome('chrome_headless/chromedriver',options=option)
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    box = soup.find_all('a',{'class':'ht-sch-btn'})
    for l in range(int(len(box)/2)):
        if l%3 == 0:
            all_links.append('https://bchl.ca' + box[l]['href'])

    team_name = soup.find_all('div',{'class':'ht-team-name'})
    team_score = soup.find_all('span',{'class':'ht-period-value ht-total'})

    counter_2 = 0
    for i in range(int(len(team_name)/2)):
        counter_2 += 1
        name = team_name[i].get_text().split("(")[0].strip().replace(' ','!')
        score = team_score[i].get_text()
        team = name + "!:!" + score
        all_scores.append(team)
    browser.quit()
    
new_date = str(date.today().strftime("%Y-%m-%d"))
function_list = [NHLScores,AHLScores,OHLScores,NCAAScores,USHLScores,OJHLScores,BCHLScores]

#Gets oldest score date from database
oldest_date = datetime.date(3000,12,31)
dates_from_database = Score.query.all()
for db_date in dates_from_database:
    date_split = db_date.date.split("-")
    db_year = int(date_split[0])
    db_month = int(date_split[1])
    db_day = int(date_split[2])
    date = datetime.date(db_year,db_month,db_day)
    if date < oldest_date:
        oldest_date = date

#Deletes oldest scores and adds todays scores to database
old_scores = Score.query.filter_by(date=oldest_date).first()
if old_scores:
    db.session.delete(old_scores)
    for function in function_list:
        function(new_date)
    all_scores = ' '.join(all_scores)
    all_links = ' '.join(all_links)
    db.session.add(Score(new_date,all_scores,all_links))
    db.session.commit()


