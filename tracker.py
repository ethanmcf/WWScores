#from enum import unique
from flask import Flask, render_template,request
#from requests.api import request
from flask_sqlalchemy import SQLAlchemy 
from datetime import date
#from sqlalchemy.orm import backref

user_name = 'Not Logged In'
id_user = ''
all_links = ''

searched_links = ''
fav_links = ''
search_scores = []
favorite_teams = []
all_scores = []
all_links = []

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=False,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    keyLogin = db.Column(db.String(20),unique=True,nullable=False)
    favorites = db.relationship('FavTeam',backref="the_user",lazy=True)

    def __init__(self,name,email,key):
        self.name=name
        self.email=email
        self.keyLogin=key
    def __repr__(self):
        return f"User('{self.name}','{self.email}','{self.keyLogin}')"

class FavTeam(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    team_name = db.Column(db.String(100),unique=False,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __init__(self,name,_id):
        self.team_name=name
        self.user_id = _id
    def __repr__(self):
        return f"FavTeam('{self.team_name}','{self.user_id}')"

class League(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    league_name = db.Column(db.String(100),unique=True,nullable=True)
    teams = db.relationship('Team',backref="the_league",lazy=True)

    def __init__(self,name):
        self.league_name=name

    def __repr__(self):
        return f"League('{self.league_name}')"

class Team(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    team_name = db.Column(db.String(100),unique=True,nullable=False)
    league_id = db.Column(db.Integer,db.ForeignKey('league.id'),nullable=False)

    def __init__(self,name,_id):
        self.team_name=name
        self.league_id = _id

    def __repr__(self):
        return f"Team('{self.team_name}','{self.league_id}')"

class Score(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.String(100),unique=False,nullable=False)
    scores = db.Column(db.Text,unique=False,nullable=True)
    links = db.Column(db.Text,unique=False,nullable=True)

    def __init__(self,date,scores,links):
        self.date = date
        self.scores = scores
        self.links = links

    def __repr__(self):
        return f"Score('{self.date}','{self.scores}','{self.links}')"

def getInfo(info):
    global all_scores,all_links
    all_info,team_lst,all_links,all_scores = [],[],[],[]
    scores = info.scores.split('|')
    links = info.links.split('|')
    #Gets scores from each league
    for score in scores:
        score = score.split(' ')
        game_lst = []
        count = 0
        for i in range(len(score)):
            if score[i] != "":
                count += 1
                team = score[i].replace('!',' ')
                all_scores.append(team)
                team_lst.append(team)
                if count == 2:
                    game_lst.append(team_lst)
                    team_lst = []
                    count = 0
        all_info.append(game_lst)
    #Gets links from each league
    for link in links:
        link = link.split(' ')
        link_lst = []
        for l in link:
            if l != "":
                all_links.append(l)
                link_lst.append(l)
        link_lst = ' '.join(link_lst)
        all_info.append(link_lst)
    return all_info

def getFavTeams(fav_teams):
    global fav_links,all_scores,all_links
    fav_links = ''
    game = []
    multiple = []
    for i in range(len(all_scores)):
        team_name = all_scores[i].split(":")[0].lower().strip()
        team_link = all_links[int(i/2)]
        for team in fav_teams:
            if team.lower().strip() == team_name:
                if len(fav_links) == 0:
                    fav_links += team_link
                elif len(fav_links) > 0:
                    fav_links += " " + team_link
                dont_append = False
                if i%2 == 0:
                    game.append(all_scores[i])
                    game.append(all_scores[i+1])
                else:
                    game.append(all_scores[i-1])
                    game.append(all_scores[i])
                for t in multiple:
                    if t[0] == game[0]:
                        dont_append = True
                if dont_append == False:
                    multiple.append(game)
                game = []
    return multiple

def searchTeam(team):
    global all_scores,all_links,searched_links
    searched_links = ''
    game = []
    multiple = []
    for i in range(len(all_scores)):
        team_name = all_scores[i].split(":")[0].lower().strip()
        team_link = all_links[int(i/2)]
        if team.lower().strip() in team_name:
            append_link = True
            for l in searched_links.split(" "):
                if team_link == l:
                    append_link = False
            if append_link == True:
                if len(searched_links) == 0:
                    searched_links += team_link
                elif len(searched_links) > 0:
                    searched_links += " " + team_link
            dont_append = False
            if i%2 == 0:
                game.append(all_scores[i])
                game.append(all_scores[i+1])
            else:
                game.append(all_scores[i-1])
                game.append(all_scores[i])
            for t in multiple:
                if t[0] == game[0]:
                    dont_append = True
            if dont_append == False:
                multiple.append(game)
            game = []
    return multiple

found_user = User('','','')
all_league = League.query.all()
all_data_teams = []
for i in range(1,8):
    all_data_teams.append(League.query.filter_by(id=str(i)).first().teams)
day = str(date.today().strftime("%Y-%m-%d"))
info_sl = Score.query.filter_by(date=day).first()

@app.route("/all-teams",methods=['POST','GET'])
def home():
    global info_sl,day
    if request.form.get('next'):
        split_day = day.split('-')
        new_day = split_day[0] + '-' + split_day[1] + '-' +str(int(split_day[2])+1)
        found_scores = Score.query.filter_by(date=new_day).first()
        if found_scores:
            day = new_day
            info_sl = found_scores
    #User Logs in
    elif request.form.get('previous'):
        split_day = day.split('-')
        new_day = split_day[0] + '-' + split_day[1] + '-' +str(int(split_day[2])-1)
        found_scores = Score.query.filter_by(date=new_day).first()
        if found_scores:
            day = new_day
            info_sl = found_scores
        
    all_info = getInfo(info_sl)
    nhl,ahl,ohl,ncaa,ushl,ojhl,bchl=all_info[0],all_info[1],all_info[2],all_info[3],all_info[4],all_info[5],all_info[6]
    nhl_links,ahl_links,ohl_links,ncaa_links,ushl_links,ojhl_links,bchl_links=all_info[7],all_info[8],all_info[9],all_info[10],all_info[11],all_info[12],all_info[13]
    return render_template("index.html",ojhl=ojhl,l_ojhl=len(ojhl), ojhl_links=ojhl_links,
                                        nhl=nhl,l_nhl=len(nhl), nhl_links=nhl_links,
                                        ncaa=ncaa,l_ncaa=len(ncaa),ncaa_links=ncaa_links,
                                        ahl = ahl, l_ahl=len(ahl),ahl_links=ahl_links,
                                        bchl=bchl,l_bchl=len(bchl),bchl_links=bchl_links,
                                        ohl=ohl,l_ohl=len(ohl),ohl_links=ohl_links,
                                        ushl=ushl,l_ushl=len(ushl),ushl_links=ushl_links,
                                        date=day)

@app.route('/',methods=['GET','POST'])
def favTeam():
    global favorite_teams,id_user,found_user,user_name,search_scores,info_sl,day
    favorites = found_user.favorites
    delete_pressed = False
    for i in range(len(favorites)):
        name = "del-btn" + str(i) 
        #Checks which del button is pressed
        if request.form.get(name):
            db.session.delete(favorites[i])
            db.session.commit()
            del favorite_teams[i]
            delete_pressed = True
    
    #Change date
    if delete_pressed == True:
        pass
    elif request.form.get('next'):
        split_day = day.split('-')
        new_day = split_day[0] + '-' + split_day[1] + '-' +str(int(split_day[2])+1)
        found_scores = Score.query.filter_by(date=new_day).first()
        if found_scores:
            day = new_day
            info_sl = found_scores
    #User Logs in
    elif request.form.get('previous'):
        split_day = day.split('-')
        new_day = split_day[0] + '-' + split_day[1] + '-' +str(int(split_day[2])-1)
        found_scores = Score.query.filter_by(date=new_day).first()
        if found_scores:
            day = new_day
            info_sl = found_scores
    elif request.form.get('logs'):
        usr = request.form['logs']
        found_user = User.query.filter_by(keyLogin=usr).first()
        if found_user:
            favorite_teams = []
            for team in found_user.favorites:
                favorite_teams.append(team.team_name)
            favs = getFavTeams(favorite_teams)
            user_name=found_user.name
            id_user = found_user.id
    #User Logs out
    elif request.form.get('log-out'):
        user_name = "Not Logged In"
        favorite_teams = []
        id_user = ''
    #User Adds Team    
    elif request.form.get('add-btn'):
        already_fav = False
        add_team = request.form['add-team'].strip().title()

        if add_team == "Niagara Icedogs":
            add_team = "Niagara IceDogs"
        elif add_team == "Ottawa 67S":
            add_team = "Ottawa 67s"
        elif add_team == "Team Usa":
            add_team = "Team USA"
        elif add_team == "American Int'l":
            add_team = 'American Int'

        for team in favorite_teams:
            if team == add_team:
                already_fav = True

        verify_team = Team.query.filter_by(team_name=add_team).first()
        if verify_team:
            if already_fav == False:
                new_fav = FavTeam(add_team,id_user)
                db.session.add(new_fav)
                db.session.commit()
                favorite_teams.append(verify_team.team_name)

    getInfo(info_sl)
    favs = getFavTeams(favorite_teams) 
    return render_template('fav.html',favs=favs,l_favs=len(favs),
                            date=day,links=fav_links,user_name=user_name,
                            fav_teams=favorite_teams,all_league=all_league,all_data_teams=all_data_teams,
                            num_favs=len(favs))

@app.route('/search-team',methods=['POST','GET'])
def teamSelect():
    if request.method == 'POST':
        team_name = request.form['search-team']
        teams = searchTeam(team_name)
    return render_template('results.html',teams=teams,res=len(teams),links=searched_links)

@app.route('/create-user',methods=['POST',"GET"])
def createUser():
    status='Enter info'
    if request.method == "POST":
        key_login = request.form.get('user-login')
        email = request.form.get('user-email')
        name = request.form.get('user-name')
        search_username = User.query.filter_by(keyLogin=key_login).first()
        search_email = User.query.filter_by(email=email).first()
        if search_username:
            status = 'Username already exists'
        elif search_email:
            status = 'Email already exists'
        elif email and name and key_login:
            new_user = User(name,email,key_login)
            db.session.add(new_user)
            db.session.commit()
            status = 'Successfully Created!'
    return render_template('create.html',status=status)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True) 
