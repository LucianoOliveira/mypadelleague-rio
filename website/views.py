from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from .models import Players, League, GameDay, LeagueClassification, Game, GameDayClassification, GameDayPlayer, ELOranking, ELOrankingHist
from . import db
import json, os
from datetime import datetime, date, timedelta
from sqlalchemy import and_, func, cast, String, text, desc, case, literal_column


views =  Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
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
    classification = LeagueClassification.query.filter_by(lc_idLeague=leagueID).order_by(desc(LeagueClassification.lc_ranking)).all()
    return render_template("league_detail.html", user=current_user, league=league_data, result=result, classification=classification) 

@views.route('/gameDay/<gameDayID>')
def gameDay_detail(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    results = Game.query.filter_by(gm_idGameDay=gameDayID).order_by(Game.gm_timeStart).all()
    classifications = GameDayClassification.query.filter_by(gc_idGameDay=gameDayID).order_by(desc(GameDayClassification.gc_ranking)).all()
    return render_template("gameDay_detail.html", user=current_user, gameDay=gameDay_data, result=results, classification=classifications) 

# management
@views.route('/managementLeague', methods=['GET', 'POST'])
@login_required
def managementLeague():
    leagues_data = League.query.order_by(League.lg_status).all()
    return render_template("managementLeague.html", user=current_user, result=leagues_data)

@views.route('/managementLeague_detail/<leagueID>', methods=['GET', 'POST'])
@login_required
def managementLeague_detail(leagueID):
    league_data = League.query.filter_by(lg_id=leagueID).first()
    result = GameDay.query.filter_by(gd_idLeague=leagueID).all()
    classification = LeagueClassification.query.filter_by(lc_idLeague=leagueID).order_by(desc(LeagueClassification.lc_ranking)).all()
    return render_template("managementLeague_detail.html", user=current_user, league=league_data, result=result, classification=classification)

@views.route('/managementPlayers', methods=['GET', 'POST'])
@login_required
def managementPlayers():
    players_data = Players.query.order_by(Players.pl_name).all()
    return render_template("managementPlayers.html", user=current_user, result=players_data)

@views.route('/rankingELO', methods=['GET', 'POST'])
@login_required
def rankingELO():
    players_data = Players.query.order_by(Players.pl_name).all()
    return render_template("rankingELO.html", user=current_user, result=players_data)

@views.route('/create_league', methods=['GET', 'POST'])
@login_required
def create_league():
    # leagues_data = League.query.order_by(League.lg_status).all()
    return render_template("create_league.html", user=current_user)

@views.route('/managementGameDay_detail/<gameDayID>')
@login_required
def managementGameDay_detail(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    results = Game.query.filter_by(gm_idGameDay=gameDayID).order_by(Game.gm_timeStart).all()
    classifications = GameDayClassification.query.filter_by(gc_idGameDay=gameDayID).order_by(desc(GameDayClassification.gc_ranking)).all()
    gameDayPlayers = GameDayPlayer.query.filter_by(gp_idGameDay=gameDayID).all()
    number_of_teamsGD = len(gameDayPlayers)
    league = League.query.filter_by(lg_id=gameDay_data.gd_idLeague).first()
    number_of_teams_league = league.lg_nbrTeams
    players_data = Players.query.order_by(Players.pl_name).all()
    league_id = league.lg_id
    gameDay_id = gameDayID
    playersGameDay = GameDayPlayer.query.filter_by(gp_idGameDay=67).order_by(GameDayPlayer.gp_team.asc(), GameDayPlayer.gp_id.asc()).all()
    # Organize players by team
    teams = {}
    for player in playersGameDay:
        if player.gp_team not in teams:
            teams[player.gp_team] = []
        teams[player.gp_team].append(player)
    return render_template("managementGameDay_detail.html", user=current_user, gameDay=gameDay_data, result=results, classification=classifications, number_of_teamsGD=number_of_teamsGD, number_of_teams_league=number_of_teams_league, players_data=players_data, gameDayPlayers=gameDayPlayers, league_id=league_id, gameDay_id=gameDay_id, teams=teams) 

@views.route('/print_page/<gameDayID>')
@login_required
def print_page(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    # TODO - Add logic for printing page
    return render_template('print_page.html', gameday=gameDay_data)

@views.route('/delete_game_day_players/<gameDayID>')
@login_required
def delete_game_day_players(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    leagueID = gameDay_data.gd_idLeague
    # DONE - Add logic for deleting game day players
    try:
        # Delete games associated with the game day
        Game.query.filter_by(gm_idGameDay=gameDayID).delete()
        # Delete game day players associated with the game day
        GameDayPlayer.query.filter_by(gp_idGameDay=gameDayID).delete()

        # Commit the changes to the database
        db.session.commit()

    except Exception as e:
        print(f"Error: {e}")
        # Handle the error, maybe log it or display a message to the user

    #Calculate the league classification after
    calculateLeagueClassification(leagueID)
    
    return redirect(url_for('views.managementGameDay_detail', gameDayID=gameDayID)) 


@views.route('/insert_game_day_players/<gameDayID>', methods=['GET', 'POST'])
@login_required
def insert_game_day_players(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    leagueID = gameDay_data.gd_idLeague
    # DONE - Add logic for inserting game day players
    league_id = request.form.get('leagueId')
    # gameDay_id = request.form.get('gameDayId')
    gameDay_id = gameDayID
    type_of_teams = request.form.get('defineTeams')
    alpha_arr = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    league_info = League.query.with_entities(League.lg_nbrTeams).filter_by(lg_id=league_id).first()
    if league_info:
        num_players = league_info[0] * 2
    else:
        num_players = 0

    # before doing anything we should delete all the players from the gameday and update classification
    func_delete_gameday_players_upd_class(gameDayID)

    # check if games are created and if not, create them
    func_create_games_for_gameday(gameDayID)

    if type_of_teams == 'ranking':
        num_rankings = LeagueClassification.query.filter_by(lc_idLeague=league_id).count()
        if num_rankings == 0:
            type_of_teams = 'random'


    # FOR RANKING *************************************************************************************
    if type_of_teams == 'ranking':
        players_array = []
        for i in range(num_players):
            id_player = i + 1
            request_player = f"player{id_player}"
            player_id = request.form[request_player]
            # Get Ranking from player
            player_ranking = 0
            try:
                ranking_info = db.session.execute(
                    text(f"SELECT lc_ranking FROM tb_leagueClassification WHERE lc_idLeague=:league_id and lc_idPlayer=:player_id"),
                    {"league_id": league_id, "player_id": player_id}
                ).fetchone()
                if ranking_info:
                    player_ranking = ranking_info[0] * 100            
            except Exception as e:
                print("Error:", e)

            # if ranking is 0 we assume age/100 as ranking
            if player_ranking==0:
                player = Players.query.filter_by(pl_id=player_id).first()
                if player:
                    # print("Reached here")
                    player_birthday = player.pl_birthday
                    player_age = calculate_player_age(player_birthday)
                    player_ranking = player_age/100  
                    # print(f"Reached here: player_age={player_age}, player_ranking={player_ranking}")              

            players_array.append({"id": player_id, "ranking": player_ranking})

        # # testing
        # print("before sort")  
        # for iy in range(0, len(players_array)):    
        #     print(players_array[iy]),  
        # # end testing
        
        players_array.sort(key=lambda x: x["ranking"], reverse=True)
        
        # # testing
        # print("after sort")  
        # for iy in range(0, len(players_array)):    
        #     print(players_array[iy]), 
        # # end testing

        try:
            # Delete all existing records on tb_gameDayPlayer
            db.session.execute(
                text(f"DELETE FROM tb_gameDayPlayer WHERE gp_idLeague=:league_id and gp_idGameDay=:gameDay_id"),
                {"league_id": league_id, "gameDay_id": gameDay_id}
            )
            db.session.commit()
        except Exception as e:
            print("Error DELETE tb_gameDayPlayer:", e)

        num_teams = num_players // 2
        for j in range(num_teams):
            team_name = chr(ord('A') + j)

            player1_result = players_array.pop(0)
            player1_team_id = player1_result['id']
            player1_team_name = Players.query.get(player1_team_id).pl_name

            player2_result = players_array.pop()
            player2_team_id = player2_result['id']
            player2_team_name = Players.query.get(player2_team_id).pl_name

            for player_id, player_name in [(player1_team_id, player1_team_name), (player2_team_id, player2_team_name)]:
                try:
                    game_day_player = GameDayPlayer(
                        gp_idLeague=league_id,
                        gp_idGameDay=gameDay_id,
                        gp_idPlayer=player_id,
                        gp_namePlayer=player_name,
                        gp_team=team_name
                    )
                    db.session.add(game_day_player)
                    db.session.commit()
                except Exception as e:
                    print("Error:", e)


            # go through all the teams in GameDayPlayer
            gd_players = GameDayPlayer.query.filter_by(gp_idGameDay=gameDay_id).order_by(GameDayPlayer.gp_team.asc(), GameDayPlayer.gp_id.asc()).all()
    
            # Organize players by team
            teams = {}
            for gd_player in gd_players:
                if gd_player.gp_team not in teams:
                    teams[gd_player.gp_team] = []
                teams[gd_player.gp_team].append(gd_player)

            
            for team, players in teams.items():
                player1ID=0
                player1Name=''
                player2ID=0
                player2Name=''
                for player in players:
                    if player1ID==0:
                        player1ID = player.gp_idPlayer
                        player1Name = player.gp_namePlayer
                    else:
                        player2ID = player.gp_idPlayer
                        player2Name = player.gp_namePlayer

                print(f"Reached here: {player1ID}, {player1Name}, {player2ID}, {player2Name}, {gameDay_id}, {team}, ")
                db.session.execute(
                text(f"update tb_game set gm_idPlayer_A1=:player1ID, gm_namePlayer_A1=:player1Name, gm_idPlayer_A2=:player2ID, gm_namePlayer_A2=:player2Name where gm_idGameDay=:gameDay_id and gm_teamA=:team"),
                    {"player1ID": player1ID, "player1Name": player1Name, "player2ID": player2ID, "player2Name": player2Name, "gameDay_id": gameDay_id, "team": team}
                )
                db.session.commit()
                db.session.execute(
                text(f"update tb_game set gm_idPlayer_B1=:player1ID, gm_namePlayer_B1=:player1Name, gm_idPlayer_B2=:player2ID, gm_namePlayer_B2=:player2Name where gm_idGameDay=:gameDay_id and gm_teamB=:team"),
                    {"player1ID": player1ID, "player1Name": player1Name, "player2ID": player2ID, "player2Name": player2Name, "gameDay_id": gameDay_id, "team": team}
                )
                db.session.commit()

    # FOR RANDOM*******************************************************************************                
    elif type_of_teams == 'random':
        # Fill the players_array with the players selected in the page
        players_array = []
        for i in range(num_players):
            id_player = i + 1
            request_player = f"player{id_player}"
            player_id = request.form[request_player]
            players_array.append(player_id)

        try:
            # Delete every player from tb_gameDayPlayer for that gameday
            GameDayPlayer.query.filter_by(gp_idLeague=league_id, gp_idGameDay=gameDay_id).delete()
            db.session.commit()
        except Exception as e:
            print("Error Delete:", e)

        import random
        random.shuffle(players_array)

        num_teams = num_players // 2
        for j in range(num_teams):
            team_name = chr(ord('A') + j)

            player1_team_id = players_array.pop(0)
            player1_team_name = Players.query.get(player1_team_id).pl_name

            player2_team_id = players_array.pop()
            player2_team_name = Players.query.get(player2_team_id).pl_name

            for player_id, player_name in [(player1_team_id, player1_team_name), (player2_team_id, player2_team_name)]:
                try:
                    game_day_player = GameDayPlayer(
                        gp_idLeague=league_id,
                        gp_idGameDay=gameDay_id,
                        gp_idPlayer=player_id,
                        gp_namePlayer=player_name,
                        gp_team=team_name
                    )
                    db.session.add(game_day_player)
                    db.session.commit()
                except Exception as e:
                    print(f"Error: {e}")

            # go through all the teams in GameDayPlayer
            gd_players = GameDayPlayer.query.filter_by(gp_idGameDay=gameDay_id).order_by(GameDayPlayer.gp_team.asc(), GameDayPlayer.gp_id.asc()).all()
    
            # Organize players by team
            teams = {}
            for gd_player in gd_players:
                if gd_player.gp_team not in teams:
                    teams[gd_player.gp_team] = []
                teams[gd_player.gp_team].append(gd_player)

            
            for team, players in teams.items():
                player1ID=0
                player1Name=''
                player2ID=0
                player2Name=''
                for player in players:
                    if player1ID==0:
                        player1ID = player.gp_idPlayer
                        player1Name = player.gp_namePlayer
                    else:
                        player2ID = player.gp_idPlayer
                        player2Name = player.gp_namePlayer

                print(f"Reached here: {player1ID}, {player1Name}, {player2ID}, {player2Name}, {gameDay_id}, {team}, ")
                db.session.execute(
                text(f"update tb_game set gm_idPlayer_A1=:player1ID, gm_namePlayer_A1=:player1Name, gm_idPlayer_A2=:player2ID, gm_namePlayer_A2=:player2Name where gm_idGameDay=:gameDay_id and gm_teamA=:team"),
                    {"player1ID": player1ID, "player1Name": player1Name, "player2ID": player2ID, "player2Name": player2Name, "gameDay_id": gameDay_id, "team": team}
                )
                db.session.commit()
                db.session.execute(
                text(f"update tb_game set gm_idPlayer_B1=:player1ID, gm_namePlayer_B1=:player1Name, gm_idPlayer_B2=:player2ID, gm_namePlayer_B2=:player2Name where gm_idGameDay=:gameDay_id and gm_teamB=:team"),
                    {"player1ID": player1ID, "player1Name": player1Name, "player2ID": player2ID, "player2Name": player2Name, "gameDay_id": gameDay_id, "team": team}
                )
                db.session.commit()

    # FOR MANUAL*************************************************************************************
    elif type_of_teams == 'manual':
        players_array = []
        for i in range(num_players):
            id_player = i + 1
            request_player = f"player{id_player}"
            player_id = request.form[request_player]
            players_array.append(player_id)

        try:
            # Delete every player from tb_gameDayPlayer for that gameday
            db.session.execute(
                text(f"DELETE FROM tb_gameDayPlayer WHERE gp_idLeague=:league_id and gp_idGameDay=:gameDay_id"),
                {"league_id": league_id, "gameDay_id": gameDay_id}
            )
            db.session.commit()
        except Exception as e:
            print("Error Delete:", e)

        num_teams = num_players // 2
        for j in range(num_teams):
            team_name = chr(ord('A') + j)

            player1_team_id = players_array.pop(0)
            player1_team_name = Players.query.get(player1_team_id).pl_name

            player2_team_id = players_array.pop(0)
            player2_team_name = Players.query.get(player2_team_id).pl_name

            for player_id, player_name in [(player1_team_id, player1_team_name), (player2_team_id, player2_team_name)]:
                try:
                    game_day_player = GameDayPlayer(
                        gp_idLeague=league_id,
                        gp_idGameDay=gameDay_id,
                        gp_idPlayer=player_id,
                        gp_namePlayer=player_name,
                        gp_team=team_name
                    )
                    db.session.add(game_day_player)
                    db.session.commit()
                except Exception as e:
                    print("Error:", e)

            # go through all the teams in GameDayPlayer
            gd_players = GameDayPlayer.query.filter_by(gp_idGameDay=gameDay_id).order_by(GameDayPlayer.gp_team.asc(), GameDayPlayer.gp_id.asc()).all()
    
            # Organize players by team
            teams = {}
            for gd_player in gd_players:
                if gd_player.gp_team not in teams:
                    teams[gd_player.gp_team] = []
                teams[gd_player.gp_team].append(gd_player)

            
            for team, players in teams.items():
                player1ID=0
                player1Name=''
                player2ID=0
                player2Name=''
                for player in players:
                    if player1ID==0:
                        player1ID = player.gp_idPlayer
                        player1Name = player.gp_namePlayer
                    else:
                        player2ID = player.gp_idPlayer
                        player2Name = player.gp_namePlayer

                print(f"Reached here: {player1ID}, {player1Name}, {player2ID}, {player2Name}, {gameDay_id}, {team}, ")
                db.session.execute(
                text(f"update tb_game set gm_idPlayer_A1=:player1ID, gm_namePlayer_A1=:player1Name, gm_idPlayer_A2=:player2ID, gm_namePlayer_A2=:player2Name where gm_idGameDay=:gameDay_id and gm_teamA=:team"),
                    {"player1ID": player1ID, "player1Name": player1Name, "player2ID": player2ID, "player2Name": player2Name, "gameDay_id": gameDay_id, "team": team}
                )
                db.session.commit()
                db.session.execute(
                text(f"update tb_game set gm_idPlayer_B1=:player1ID, gm_namePlayer_B1=:player1Name, gm_idPlayer_B2=:player2ID, gm_namePlayer_B2=:player2Name where gm_idGameDay=:gameDay_id and gm_teamB=:team"),
                    {"player1ID": player1ID, "player1Name": player1Name, "player2ID": player2ID, "player2Name": player2Name, "gameDay_id": gameDay_id, "team": team}
                )
                db.session.commit()
    
    return redirect(url_for('views.managementGameDay_detail', gameDayID=gameDayID)) 


@views.route('/player_detail/<playerID>')
def player_detail(playerID):
    current_Player = Players.query.filter_by(pl_id=playerID).first()
    num_game_day_won = db.session.query(func.count()).filter(
        (GameDay.gd_idWinner1 == playerID) | (GameDay.gd_idWinner2 == playerID)
    ).scalar()
    if num_game_day_won>0:
        num_game_day_won_text = f"Vencedor de {num_game_day_won} eventos!"
    else:
        num_game_day_won_text = f"Ainda não venceu nenhum evento!"
    
    last_game_date = db.session.query(Game.gm_date).filter(
        (Game.gm_idPlayer_A1 == playerID) |
        (Game.gm_idPlayer_A2 == playerID) |
        (Game.gm_idPlayer_B1 == playerID) |
        (Game.gm_idPlayer_B2 == playerID)
    ).order_by(Game.gm_date.desc()).first()
    last_game_date_string = last_game_date[0].strftime('%Y-%m-%d')

    # All games
    try:
        games_query = db.session.query(
            Game.gm_timeStart,
            Game.gm_timeEnd,
            Game.gm_court,
            Game.gm_namePlayer_A1,
            Game.gm_namePlayer_A2,
            Game.gm_result_A,
            Game.gm_result_B,
            Game.gm_namePlayer_B1,
            Game.gm_namePlayer_B2,
            Game.gm_id,
            Game.gm_idPlayer_A1,
            Game.gm_idPlayer_A2,
            Game.gm_idPlayer_B1,
            Game.gm_idPlayer_B2,
            Game.gm_date,
            (ELOrankingHist.el_afterRank - ELOrankingHist.el_beforeRank).label('gm_points_var')
        ).join(
            ELOrankingHist, ELOrankingHist.el_gm_id == Game.gm_id
        ).filter(
            (Game.gm_idPlayer_A1 == playerID) |
            (Game.gm_idPlayer_A2 == playerID) |
            (Game.gm_idPlayer_B1 == playerID) |
            (Game.gm_idPlayer_B2 == playerID),
            (Game.gm_result_A > 0) | (Game.gm_result_B > 0)
        ).order_by(
            Game.gm_date.desc(), Game.gm_timeStart.desc()
        ).all()
    except Exception as e:
        print(f"Error: {str(e)}")

    #Gem games won, lost and totals
    try:
        player_stats = db.session.query(
            ELOranking.pl_wins.label('games_won'),
            ELOranking.pl_losses.label('games_lost'),
            ELOranking.pl_totalGames.label('total_games')
        ).filter(
            ELOranking.pl_id == playerID
        ).first()
    except Exception as e:
        print(f"Error: {str(e)}")

    #Best TeamMate
    try:
        subquery = db.session.query(
            case(
                (and_(Game.gm_idPlayer_A1 == playerID, Game.gm_idPlayer_A2)),
                (and_(Game.gm_idPlayer_A2 == playerID, Game.gm_idPlayer_A1)),
                (and_(Game.gm_idPlayer_B1 == playerID, Game.gm_idPlayer_B2)),
                (and_(Game.gm_idPlayer_B2 == playerID, Game.gm_idPlayer_B1))
            ).label('teamMate'),
            case(
                (and_(Game.gm_idPlayer_A1 == playerID) & (Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                (and_(Game.gm_idPlayer_B1 == playerID) & (Game.gm_result_B > Game.gm_result_A), literal_column("1")),
                (and_(Game.gm_idPlayer_A2 == playerID) & (Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                (and_(Game.gm_idPlayer_B2 == playerID) & (Game.gm_result_B > Game.gm_result_A), literal_column("1"))
            ).label('won'),
            case(
                (and_(Game.gm_idPlayer_A1 == playerID) & (Game.gm_result_B > Game.gm_result_A), literal_column("1")),
                (and_(Game.gm_idPlayer_B1 == playerID) & (Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                (and_(Game.gm_idPlayer_A2 == playerID) & (Game.gm_result_B > Game.gm_result_A), literal_column("1")),
                (and_(Game.gm_idPlayer_B2 == playerID) & (Game.gm_result_A > Game.gm_result_B), literal_column("1"))
            ).label('lost')
        ).filter(
            (Game.gm_idPlayer_A1 == playerID) |
            (Game.gm_idPlayer_A2 == playerID) |
            (Game.gm_idPlayer_B1 == playerID) |
            (Game.gm_idPlayer_B2 == playerID),
            (Game.gm_result_A > 0) | (Game.gm_result_B > 0)
        ).subquery()

        best_teammate = db.session.query(
            Players.pl_name,
            func.sum(subquery.c.won) / func.count(subquery.c.teamMate).label('winPerc'),
            func.sum(subquery.c.won).label('won'),
            func.count(subquery.c.teamMate).label('totalgames')
        ).join(
            subquery, subquery.c.teamMate == Players.pl_id
        ).filter(
            Players.pl_ranking_stat == 'Y'
        ).group_by(
            subquery.c.teamMate
        ).order_by(
            desc(func.sum(subquery.c.won) / func.count(subquery.c.teamMate)),
            desc(func.sum(subquery.c.won))
        ).limit(1).first()

    except Exception as e:
        print(f"Error: {str(e)}")

    # TODO - Get data from games to complete user data
    player_data = {
        "player_id": current_Player.pl_id,
        "player_name": current_Player.pl_name,
        "player_email": current_Player.pl_email,
        "player_birthday": current_Player.pl_birthday,
        "numGameDayWins": num_game_day_won_text,
        "lastGamePlayed": last_game_date_string,
        "games_won": 50,
        "total_games": 100,
        "best_teammate_name": str(best_teammate[0]),
        "best_teammate_win_percentage": best_teammate[1]*100,
        "best_teammate_total_games": best_teammate[3],
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
    return render_template("player_detail.html", user=current_user, player=player_data, results=games_query, getPlayerStats=player_stats, best_teammate=best_teammate)   


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


@views.route('/submitResultsGameDay/<gameDayID>', methods=['GET', 'POST'])
@login_required
def submitResultsGameDay(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    league_id = gameDay_data.gd_idLeague
    # league_id = request.form.get('leagueId')
    #Get all ids of that gameday
    result = Game.query.filter_by(gm_idGameDay=gameDayID).all()
    if result:
        for data in result:
            resultA = f"resultGameA{data.gm_id}"
            resultB = f"resultGameB{data.gm_id}"
            gameID = data.gm_id
            getResultA = request.form.get(resultA)
            getResultB = request.form.get(resultB)
            db.session.execute(
            text(f"update tb_game set gm_result_A=:getResultA, gm_result_B=:getResultB where gm_id=:gameID and gm_idLeague=:league_id"),
                {"getResultA": getResultA, "getResultB": getResultB, "gameID": gameID, "league_id": league_id}
            )
            db.session.commit()

        db.session.execute(
        text(f"update tb_gameday SET gd_status='Terminado' where gd_id=:gameDayID and gd_idLeague=:league_id"),
            {"gameDayID": gameDayID, "league_id": league_id}
        )
        db.session.commit()

        #If all gamedays of that league are Terminado  change status of League to Terminado
        ended_game_days_count = GameDay.query.filter_by(gd_idLeague=league_id, gd_status='Por Jogar').count()

        if ended_game_days_count == 0:
            # Update the league status to 'Terminado'
            league = League.query.get(league_id)
            league.lg_status = '8 - Terminado'
            db.session.commit()

        calculateGameDayClassification(gameDayID)
        calculateLeagueClassification(league_id)

    return redirect(url_for('views.managementGameDay_detail', gameDayID=gameDayID)) 


def calculateLeagueClassification(leagueID):
    print("Enter LeagueClassification")
    # clear the league classification
    try:
        LeagueClassification.query.filter_by(lc_idLeague=leagueID).delete()
        db.session.commit()

        players_query = Players.query.filter(Players.pl_id.in_(db.session.query(GameDayPlayer.gp_idPlayer).filter(GameDayPlayer.gp_idLeague == leagueID).group_by(GameDayPlayer.gp_idPlayer)))
        players_data = players_query.all()


        for player in players_data:
            id_player = player.pl_id
            player_name = player.pl_name
            player_birthday = player.pl_birthday
            player_age = calculate_player_age(player_birthday)

            games_info_query = Game.query.filter(Game.gm_idLeague == leagueID, ((Game.gm_idPlayer_A1 == id_player) | (Game.gm_idPlayer_A2 == id_player) | (Game.gm_idPlayer_B1 == id_player) | (Game.gm_idPlayer_B2 == id_player)), ((Game.gm_result_A > 0) | (Game.gm_result_B > 0)))
            games_info = games_info_query.first()

            if games_info:
                subquery = (
                    db.session.query(
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("3")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("3")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("3")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("3")),
                            else_=None
                        ).label("POINTS"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player), Game.gm_result_A),
                            (and_(Game.gm_idPlayer_A2 == id_player), Game.gm_result_A),
                            (and_(Game.gm_idPlayer_B1 == id_player), Game.gm_result_B),
                            (and_(Game.gm_idPlayer_B2 == id_player), Game.gm_result_B),
                            else_=None
                        ).label("GAMESFAVOR"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player), Game.gm_result_B),
                            (and_(Game.gm_idPlayer_A2 == id_player), Game.gm_result_B),
                            (and_(Game.gm_idPlayer_B1 == id_player), Game.gm_result_A),
                            (and_(Game.gm_idPlayer_B2 == id_player), Game.gm_result_A),
                            else_=None
                        ).label("GAMESAGAINST"),
                        literal_column("1").label("GAMES"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            else_=None
                        ).label("WINS"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            else_=None
                        ).label("LOSSES")
                    )
                    .filter(Game.gm_idLeague == leagueID, (Game.gm_idPlayer_A1 == id_player) | (Game.gm_idPlayer_A2 == id_player) | (Game.gm_idPlayer_B1 == id_player) | (Game.gm_idPlayer_B2 == id_player))
                    .subquery("TOTALS")
                )

                query = (
                    db.session.query(
                        literal_column(str(leagueID)).label("LEAGUEID"),
                        literal_column(str(id_player)).label("PLAYERID"),
                        literal_column(f"'{player_name}'").label("PLAYERNAME"), 
                        # TODO - if it is to give one point per participation leave like this, otherwise get this in a config file
                        (func.sum(subquery.c.POINTS)+(func.sum(subquery.c.GAMES)/3)).label("POINTS"),
                        func.sum(subquery.c.WINS).label("WINS"),
                        func.sum(subquery.c.LOSSES).label("LOSSES"),
                        func.sum(subquery.c.GAMESFAVOR).label("GAMESFAVOR"),
                        func.sum(subquery.c.GAMESAGAINST).label("GAMESAGAINST"),
                        (func.sum(subquery.c.GAMESFAVOR) - func.sum(subquery.c.GAMESAGAINST)).label("GAMESDIFFERENCE"),
                        (
                            ((func.sum(subquery.c.POINTS) + func.sum(subquery.c.GAMES) / 3) * 100000) +
                            ((func.sum(subquery.c.WINS) / func.sum(subquery.c.GAMES)) * 10000) +
                            ((func.sum(subquery.c.GAMESFAVOR) / (func.sum(subquery.c.GAMESFAVOR) + func.sum(subquery.c.GAMESAGAINST))) * 100) +
                            (player_age / 100)
                        ).label("RANKING")
                    )
                    .select_from(subquery)
                    .group_by("LEAGUEID", "PLAYERID", "PLAYERNAME")
                )

                result = query.all()

                for r2 in result:
                    # Write Classification
                    classification = LeagueClassification(
                        lc_idLeague=leagueID,
                        lc_idPlayer=r2.PLAYERID,
                        lc_namePlayer=r2.PLAYERNAME,
                        lc_points=r2.POINTS or 0,
                        lc_wins=r2.WINS or 0,
                        lc_losses=r2.LOSSES or 0,
                        lc_gamesFavor=r2.GAMESFAVOR or 0,
                        lc_gamesAgainst=r2.GAMESAGAINST or 0,
                        lc_gamesDiff=r2.GAMESDIFFERENCE or 0,
                        lc_ranking=r2.RANKING or 0,
                    )
                    db.session.add(classification)

                # Commit the changes to the database
                db.session.commit()

            else:
                # Calculation for players without games
                # Write Classification
                classification = LeagueClassification(
                    lc_idLeague=leagueID,
                    lc_idPlayer=id_player,
                    lc_namePlayer=player_name,
                    lc_points=0,
                    lc_wins=0,
                    lc_losses=0,
                    lc_gamesFavor=0,
                    lc_gamesAgainst=0,
                    lc_gamesDiff=0,
                    lc_ranking=0+(player_age/100),
                )
                db.session.add(classification)
                db.session.commit()

        # Commit the changes to the database
        db.session.commit()

    except Exception as e:
        print(f"Error: {e}")
        # Handle the error, maybe log it or display a message to the user


def calculateGameDayClassification(gameDayID):
    print("Enter GameDayClassification")
    # clear the league classification
    gameDay = GameDay.query.filter_by(gd_id=gameDayID).first()
    leagueID = gameDay.gd_idLeague
    try:
        GameDayClassification.query.filter_by(gc_idGameDay=gameDayID).delete()
        db.session.commit()

        players_query = Players.query.filter(Players.pl_id.in_(db.session.query(GameDayPlayer.gp_idPlayer).filter(GameDayPlayer.gp_idGameDay == gameDayID).group_by(GameDayPlayer.gp_idPlayer)))
        players_data = players_query.all()


        for player in players_data:
            print(player)
            id_player = player.pl_id
            player_name = player.pl_name
            player_birthday = player.pl_birthday
            player_age = calculate_player_age(player_birthday)

            games_info_query = Game.query.filter(Game.gm_idGameDay == gameDayID, ((Game.gm_idPlayer_A1 == id_player) | (Game.gm_idPlayer_A2 == id_player) | (Game.gm_idPlayer_B1 == id_player) | (Game.gm_idPlayer_B2 == id_player)), ((Game.gm_result_A > 0) | (Game.gm_result_B > 0)))
            games_info = games_info_query.first()

            if games_info:
                subquery = (
                    db.session.query(
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("3")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("3")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("3")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("3")),
                            else_=None
                        ).label("POINTS"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player), Game.gm_result_A),
                            (and_(Game.gm_idPlayer_A2 == id_player), Game.gm_result_A),
                            (and_(Game.gm_idPlayer_B1 == id_player), Game.gm_result_B),
                            (and_(Game.gm_idPlayer_B2 == id_player), Game.gm_result_B),
                            else_=None
                        ).label("GAMESFAVOR"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player), Game.gm_result_B),
                            (and_(Game.gm_idPlayer_A2 == id_player), Game.gm_result_B),
                            (and_(Game.gm_idPlayer_B1 == id_player), Game.gm_result_A),
                            (and_(Game.gm_idPlayer_B2 == id_player), Game.gm_result_A),
                            else_=None
                        ).label("GAMESAGAINST"),
                        literal_column("1").label("GAMES"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            else_=None
                        ).label("WINS"),
                        case(
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_A1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_A2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A > Game.gm_result_B), literal_column("1")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A == Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B1 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            (and_(Game.gm_idPlayer_B2 == id_player, Game.gm_result_A < Game.gm_result_B), literal_column("0")),
                            else_=None
                        ).label("LOSSES")
                    )
                    .filter(Game.gm_idGameDay == gameDayID, (Game.gm_idPlayer_A1 == id_player) | (Game.gm_idPlayer_A2 == id_player) | (Game.gm_idPlayer_B1 == id_player) | (Game.gm_idPlayer_B2 == id_player))
                    .subquery("TOTALS")
                )
                
                query = (
                    db.session.query(
                        literal_column(str(leagueID)).label("LEAGUEID"),
                        literal_column(str(gameDayID)).label("GAMEDAYID"),
                        literal_column(str(id_player)).label("PLAYERID"),
                        literal_column(f"'{player_name}'").label("PLAYERNAME"), 
                        # TODO - if it is to give one point per participation leave like this, otherwise get this in a config file
                        (func.sum(subquery.c.POINTS)+(func.sum(subquery.c.GAMES)/3)).label("POINTS"),
                        func.sum(subquery.c.WINS).label("WINS"),
                        func.sum(subquery.c.LOSSES).label("LOSSES"),
                        func.sum(subquery.c.GAMESFAVOR).label("GAMESFAVOR"),
                        func.sum(subquery.c.GAMESAGAINST).label("GAMESAGAINST"),
                        (func.sum(subquery.c.GAMESFAVOR) - func.sum(subquery.c.GAMESAGAINST)).label("GAMESDIFFERENCE"),
                        (
                            ((func.sum(subquery.c.POINTS) + func.sum(subquery.c.GAMES) / 3) * 100000) +
                            ((func.sum(subquery.c.WINS)) +
                            # ((func.sum(subquery.c.WINS) / func.sum(subquery.c.GAMES)) * 10000) +
                            # ((func.sum(subquery.c.GAMESFAVOR) / (func.sum(subquery.c.GAMESFAVOR) + func.sum(subquery.c.GAMESAGAINST))) * 100) +
                            (player_age / 100)
                        ).label("RANKING")
                    )
                    .select_from(subquery)
                    .group_by("GAMEDAYID", "PLAYERID", "PLAYERNAME")
                )
                print(f"query: {query}")
                result = query.all()
                print(f"result: {result}")

                for r2 in result:
                    print(r2)
                    # Write Classification
                    classification = GameDayClassification(
                        gc_idLeague=leagueID,
                        gc_idGameDay=gameDayID,
                        gc_idPlayer=r2.PLAYERID,
                        gc_namePlayer=r2.PLAYERNAME,
                        gc_points=r2.POINTS or 0,
                        gc_wins=r2.WINS or 0,
                        gc_losses=r2.LOSSES or 0,
                        gc_gamesFavor=r2.GAMESFAVOR or 0,
                        gc_gamesAgainst=r2.GAMESAGAINST or 0,
                        gc_gamesDiff=r2.GAMESDIFFERENCE or 0,
                        gc_ranking=r2.RANKING or 0,
                    )
                    db.session.add(classification)

                # Commit the changes to the database
                db.session.commit()

            else:
                # Calculation for players without games
                # Write Classification
                classification = GameDayClassification(
                    gc_idLeague=leagueID,
                    gc_idGameDay=gameDayID,
                    gc_idPlayer=id_player,
                    gc_namePlayer=player_name,
                    gc_points=0,
                    gc_wins=0,
                    gc_losses=0,
                    gc_gamesFavor=0,
                    gc_gamesAgainst=0,
                    gc_gamesDiff=0,
                    gc_ranking=0+(player_age/100),
                )
                db.session.add(classification)
                db.session.commit()

        # Commit the changes to the database
        db.session.commit()

    except Exception as e:
        print(f"Error: {e}")
        # Handle the error, maybe log it or display a message to the user

    print("Reached Finally")
    # Finally we need to update the winners
    winners_query = (
        db.session.query(
            GameDayClassification.gc_idPlayer.label('idPlayer'),
            GameDayClassification.gc_namePlayer.label('namePlayer')
        )
        .filter(GameDayClassification.gc_idLeague == leagueID)
        .filter(GameDayClassification.gc_idGameDay == gameDayID)
        .order_by(GameDayClassification.gc_ranking.desc())
        .limit(2)
        .subquery()
    )

    # Fetch the first winner
    winner1 = (
        db.session.query(winners_query.c.idPlayer, winners_query.c.namePlayer)
        .order_by(winners_query.c.idPlayer.asc())
        .first()
    )

    # Fetch the second winner
    winner2 = (
        db.session.query(winners_query.c.idPlayer, winners_query.c.namePlayer)
        .order_by(winners_query.c.idPlayer.desc())
        .first()
    )

    # Update winners to tb_gameday
    gameday_update_query = (
        db.session.query(GameDay)
        .filter(GameDay.gd_idLeague == leagueID)
        .filter(GameDay.gd_id == gameDayID)
        .update(
            {
                GameDay.gd_idWinner1: winner1.idPlayer,
                GameDay.gd_nameWinner1: winner1.namePlayer,
                GameDay.gd_idWinner2: winner2.idPlayer,
                GameDay.gd_nameWinner2: winner2.namePlayer
            }
        )
    )

    # Commit the changes
    db.session.commit()
    print("Ended Finally")


    
def calculate_player_age(birthdate):
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age


def func_delete_gameday_players_upd_class(gameDayID):
    gameDay_data = GameDay.query.filter_by(gd_id=gameDayID).first()
    leagueID = gameDay_data.gd_idLeague
    # DONE - Add logic for deleting game day players
    try:
        # Delete games associated with the game day
        Game.query.filter_by(gm_idGameDay=gameDayID).delete()
        # Delete game day players associated with the game day
        GameDayPlayer.query.filter_by(gp_idGameDay=gameDayID).delete()

        # Commit the changes to the database
        db.session.commit()

    except Exception as e:
        print(f"Error: {e}")
        # Handle the error, maybe log it or display a message to the user

    #Calculate the league classification after
    calculateLeagueClassification(leagueID)
    
def func_create_games_for_gameday(gameDayID):
    #CHECK IF IN tb_game there are already all the games necessary
    GameD = GameDay.query.filter_by(gd_id=gameDayID).first()
    league = League.query.filter_by(lg_id=GameD.gd_idLeague).first()
    league_nbrTeams= league.lg_nbrTeams
    startTime = league.lg_startTime
    league_minWarmUp = league.lg_minWarmUp
    league_minPerGame = league.lg_minPerGame
    league_minBetweenGames = league.lg_minBetweenGames
    leagueId = league.lg_id
    gameDay_Day = GameD.gd_date

    if league_nbrTeams == 2:
        necessary_games = 1
    elif league_nbrTeams == 3:
        necessary_games = 3
    elif league_nbrTeams == 4:
        necessary_games = 6
    elif league_nbrTeams == 5:
        necessary_games = 10
    elif league_nbrTeams == 6:
        necessary_games = 15
    elif league_nbrTeams == 7:
        necessary_games = 21
    elif league_nbrTeams == 8:
        necessary_games = 28
    else:
        necessary_games = 0

    # $gameStart = date('H:i:s', strtotime("+".$league_minWarmUp." minutes", strtotime($startTime)));
    # $gameEnd = date('H:i:s', strtotime("+".$league_minPerGame." minutes", strtotime($gameStart)));
    # Assuming you have startTime as a datetime object, league_minWarmUp, and league_minPerGame as integers
    strTime = datetime.strptime(str(startTime), "%H:%M:%S")  # Convert startTime to datetime if needed

    # Add league_minWarmUp minutes to startTime
    gameStart = strTime + timedelta(minutes=league_minWarmUp)

    # Add league_minPerGame minutes to gameStart
    gameEnd = gameStart + timedelta(minutes=league_minPerGame)

    # Convert gameStart and gameEnd to string format 'H:i:s'
    gameStart_str = gameStart.strftime("%H:%M:%S")
    gameEnd_str = gameEnd.strftime("%H:%M:%S")  
    gameDay_Day_str = gameDay_Day.strftime("%Y-%m-%d")
    print(gameDay_Day_str)
                               
                                       
    # if there are games but the number of games is not the same as the necessary delete all the games
    num_games = Game.query.filter_by(gm_idGameDay=gameDayID).count()
    if num_games != necessary_games:
        Game.query.filter_by(gm_idGameDay=gameDayID).delete()
        # Commit the changes to the database
        db.session.commit()
        num_games = 0

    # if there aren't any games or if they were deleted in the last step create all the necessary games
    if num_games == 0:
        if league_nbrTeams == 2:
            necessary_games = 1
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
        
        elif league_nbrTeams == 3:
            necessary_games = 3
            # Game 1
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 2
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'B', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 3
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'C', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
        
        elif league_nbrTeams == 4:
            necessary_games = 6
            # Game 1 and 2
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'C', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 3 and 4
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'B', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 5 and 6
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'B', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()

        elif league_nbrTeams == 5:
            necessary_games = 10
            # Game 1 and 2
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'B', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 3 and 4
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'C', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'D', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 5 and 6
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'E', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'A', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 7 and 8
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'B', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'C', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 9 and 10
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'D', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'E', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
        
        elif league_nbrTeams == 6:
            necessary_games = 15
            # Game 1, 2 and 3 ROUND 1
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'B', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'C', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'D', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 4, 5 and 6 ROUND 2
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'C', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'F', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'B', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 7, 8 and 9 ROUND 3
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'F', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'B', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'A', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 10, 11 and 12 ROUND 4
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'D', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'E', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'F', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 13, 14 and 15 ROUND 5
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'E', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'A', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'D', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            
        elif league_nbrTeams == 7:
            necessary_games = 21
            # Game 1, 2 and 3 ROUND 1
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'B', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'C', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 4, 5 and 6 ROUND 2
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'D', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'E', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'F', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 7, 8 and 9 ROUND 3
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'B', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'C', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'D', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 10, 11 and 12 ROUND 4
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'E', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'F', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'G', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # Game 13, 14 and 15 ROUND 5
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'C', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'D', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'E', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 6
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'F', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'G', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'A', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 7
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'G', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'A', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'B', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()

        elif league_nbrTeams == 8:
            necessary_games = 28
            # ROUND 1
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'B', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'C', 'H')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'D', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'E', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 2
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'C', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'A', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'H', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'B', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 3
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'F', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'G', 'H')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'D', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'E', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 4
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'G', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'H', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'B', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'F', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 5
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'A', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'D', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'E', 'H')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'F', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 6
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'D', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'H', 'A')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'B', 'G')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'C', 'F')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            # ROUND 7
            gameStart = gameEnd + timedelta(minutes=league_minBetweenGames)
            gameEnd = gameStart + timedelta(minutes=league_minPerGame)
            gameStart_str = gameStart.strftime("%H:%M:%S")
            gameEnd_str = gameEnd.strftime("%H:%M:%S")  
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 1', 0, 0, 'G', 'C')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 2', 0, 0, 'H', 'B')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 3', 0, 0, 'A', 'E')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            db.session.execute(
                text(f"INSERT INTO tb_game (gm_idLeague, gm_idGameDay, gm_date, gm_timeStart, gm_timeEnd, gm_court, gm_result_A, gm_result_B, gm_teamA, gm_teamB) VALUES (:league_id, :gameDay_id, :gameday_day, :gameStart, :gameEnd, 'Campo 4', 0, 0, 'F', 'D')"),
                {"league_id": leagueId, "gameDay_id": gameDayID, "gameday_day": gameDay_Day_str, "gameStart": gameStart_str, "gameEnd": gameEnd_str}
            )
            db.session.commit()
            
        else:
            necessary_games = 0