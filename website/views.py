from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from .models import Players, League, GameDay
from . import db
import json, os
from datetime import datetime, date, timedelta
from sqlalchemy import and_, func, cast, String, text


views =  Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():

    # leagues_query = text("""
    #     SELECT lg_id, lg_name, lg_startDate, lg_endDate,
    #            SUBSTRING(lg_status, 4) AS lg_status1, lg_level
    #     FROM tb_league
    #     ORDER BY lg_status ASC, lg_startDate DESC, lg_id DESC
    # """)
    # leagues_data = db.session.execute(leagues_query).fetchall()
    leagues_data = League.query.order_by(League.lg_status).all()
    return render_template("index.html", user=current_user, result=leagues_data)

@views.route('/players', methods=['GET', 'POST'])
def players():
    players_data = Players.query.order_by(Players.pl_name).all()
    return render_template('players.html', user=current_user, players=players_data)

@views.route('/league/<leagueID>')
def league_detail(leagueID):
    league_data = League.query.filter_by(lg_id=leagueID).first()
    result = GameDay.query.filter_by(gd_idLeague=leagueID).all()
    return render_template("league_detail.html", user=current_user, league=league_data, result=result) 

@views.route('/gameDay/<gameDayID>')
def gameDay_detail(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    return render_template("gameday_detail.html", user=current_user, gameDay=gameDay_data) 

@views.route('/player_detail/<playerID>')
def player_detail(playerID):
    current_Player = Players.query.filter_by(pl_id=playerID).first()
    # TODO - Get data from games to complete user data
    player_data = {
        "player_id": current_Player.pl_id,
        "player_name": current_Player.pl_name,
        "player_email": current_Player.pl_email,
        "player_birthday": current_Player.pl_birthday,
        "numGameDayWins": "Venceu 2 NonStop",
        "lastGamePlayed": "2024-01-02",
        "games_won": 50,
        "total_games": 100,
        "best_teammate_name": "Best Team Mate",
        "best_teammate_win_percentage": 100.0,
        "best_teammate_total_games": 11,
        "worst_teammate_name": "Worst Team Mate",
        "worst_teammate_lost_percentage": 75.0,
        "worst_teammate_total_games": 4,
        "worst_nightmare_name": "Worst Nightmare",
        "worst_nightmare_lost_percentage": 80.0,
        "worst_nightmare_games": 10,
        "best_opponent_name": "Best Opponent",
        "best_opponent_victory_percentage": 100.0,
        "best_opponent_games": 5
    }
    return render_template("player_detail.html", user=current_user, player=player_data)   


@views.route('/display_user_image/<userID>')
def display_user_image(userID):
    filePath = str(os.path.abspath(os.path.dirname(__file__)))+'/static/photos/users/'+str(userID)+'/main.jpg'
    if os.path.isfile(filePath):
        return redirect(url_for('static', filename='photos/users/'+ str(userID)+'/main.jpg'), code=301)
    else:
        return redirect(url_for('static', filename='photos/users/nophoto.jpg'), code=301)
    

@views.route('/display_league_image_big/<leagueID>')
def display_league_image_big(leagueID):
    filePath = str(os.path.abspath(os.path.dirname(__file__)))+'/static/photos/leagues/'+str(leagueID)+'.jpg'
    if os.path.isfile(filePath):
        return redirect(url_for('static', filename='photos/leagues/'+ str(leagueID)+'.jpg'), code=301)
    else:
        return redirect(url_for('static', filename='photos/leagues/nophoto.jpg'), code=301)
    
@views.route('/display_league_image_small/<leagueID>')
def display_league_image_small(leagueID):
    filePath = str(os.path.abspath(os.path.dirname(__file__)))+'/static/photos/leagues/'+str(leagueID)+'s.jpg'
    if os.path.isfile(filePath):
        return redirect(url_for('static', filename='photos/leagues/'+ str(leagueID)+'s.jpg'), code=301)
    else:
        return redirect(url_for('static', filename='photos/leagues/nophotoS.jpg'), code=301)    


    