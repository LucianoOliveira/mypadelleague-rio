from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from .models import Players
from . import db
import json, os
from datetime import datetime, date, timedelta
from sqlalchemy import and_, func, cast, String


views =  Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html", user=current_user)

@views.route('/players', methods=['GET', 'POST'])
def players():
        # Check if there are no records in the Players table
    if Players.query.count() == 0:
        print("Inserting players into the database...")
        players_data = [
            {"pl_id": 1,  "pl_name": "Miguel Pinto", 		  "pl_acron": "MPI", "pl_email": "", 							"pl_pwd": None,  "pl_birthday": date(2000,  8, 21), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 2,  "pl_name": "Gonçalo Lopes", 		  "pl_acron": "GLO", "pl_email": "", 							"pl_pwd": None,  "pl_birthday": date(1999,  1,  8), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 3,  "pl_name": "Luciano Oliveira", 	  "pl_acron": "LOL", "pl_email": "luciano8.oliveira@gmail.com", "pl_pwd": None,  "pl_birthday": date(1983,  1,  7), "pl_type": "Root", 	"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 4,  "pl_name": "Joel Silva", 			  "pl_acron": "JSI", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1987,  5, 14), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 5,  "pl_name": "Pedro Araújo", 		  "pl_acron": "PAR", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1986,  8,  7), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 6,  "pl_name": "Tiago Silva", 		  "pl_acron": "TSI", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1990,  3, 12), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 7,  "pl_name": "Rafael Gomes", 		  "pl_acron": "RGO", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1968, 12,  9), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 8,  "pl_name": "Tiago Martins", 		  "pl_acron": "TMA", "pl_email": "",                            "pl_pwd": None,  "pl_birthday": date(1979,  5, 28), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 9,  "pl_name": "Hugo Lima", 			  "pl_acron": "HLI", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1985,  1, 28), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 10, "pl_name": "Zézé Seixas", 		  "pl_acron": "ZSE", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1971,  2, 18), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 11, "pl_name": "Rui Areal", 			  "pl_acron": "RAR", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1980,  1,  1), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 12, "pl_name": "Luis Gonçalves", 		  "pl_acron": "LGO", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1990,  8, 29), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 13, "pl_name": "Rui Filipe", 			  "pl_acron": "RFI", "pl_email": "",                            "pl_pwd": None,  "pl_birthday": date(1976,  9,  5), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 14, "pl_name": "Natalino Oliveira", 	  "pl_acron": "NOL", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1958,  3, 31), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 15, "pl_name": "José Torres", 		  "pl_acron": "JTO", "pl_email": None,                          "pl_pwd": None,  "pl_birthday": date(1999,  5, 10), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 17, "pl_name": "Cláudio Ribeiro", 	  "pl_acron": "CRI", "pl_email": "",                            "pl_pwd": None,  "pl_birthday": date(1977,  7, 17), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 18, "pl_name": "Ricardo Silva", 		  "pl_acron": "RSI", "pl_email": "rjcs9271@gmail.com",          "pl_pwd": None,  "pl_birthday": date(1981,  7, 10), "pl_type": "Super", 	"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 19, "pl_name": "David Santos", 		  "pl_acron": "DSA", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1978,  3, 27), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 20, "pl_name": "Jean-Jacques", 		  "pl_acron": "JJA", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1970, 10, 23), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 21, "pl_name": "Nuno Rodrigues", 		  "pl_acron": "NRO", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1988, 10,  3), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 22, "pl_name": "João Cunha", 			  "pl_acron": "JCU", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1982,  7,  1), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 23, "pl_name": "Telmo Oliveira", 		  "pl_acron": "TOL", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1986,  1, 16), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 24, "pl_name": "Rafael Gonçalves", 	  "pl_acron": "RGN", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1980, 11,  6), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 25, "pl_name": "Miguel Pereira", 		  "pl_acron": "MPE", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1978,  4,  4), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 26, "pl_name": "Idalino Freitas", 	  "pl_acron": "IFR", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1974,  6, 27), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 27, "pl_name": "Alexandre Sobral", 	  "pl_acron": "ASO", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1991,  2,  7), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 28, "pl_name": "Hugo Dias", 			  "pl_acron": "HDI", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1989,  5, 25), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 29, "pl_name": "Miguel Pinheiro", 	  "pl_acron": "MPI", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1975,  8, 18), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 32, "pl_name": "Ana Silva", 			  "pl_acron": "ASI", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1988,  2,  3), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 33, "pl_name": "Pedro Pimenta", 		  "pl_acron": "PPI", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1985,  8, 20), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 34, "pl_name": "Zé Pedro", 			  "pl_acron": "ZPE", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1989, 11, 22), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 35, "pl_name": "Tiago Pinheiro", 		  "pl_acron": "TPI", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2006,  3, 30), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 36, "pl_name": "Honorato Coelho", 	  "pl_acron": "HCO", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1977,  5, 28), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 37, "pl_name": "Manuel Ferreira", 	  "pl_acron": "MFE", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1980,  4,  8), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 38, "pl_name": "Ana Isabel Faria", 	  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1981,  6,  5), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 39, "pl_name": "Vitor Oliveira", 		  "pl_acron": "VOL", "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1989,  5, 31), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 40, "pl_name": "Daniel Silva", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1984,  1, 27), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 41, "pl_name": "Tiago Rocha", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1996,  7,  4), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 42, "pl_name": "Flávio Almeida", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1995,  5,  9), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 44, "pl_name": "Jorge Martins", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1996,  3,  7), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 45, "pl_name": "Tiago Miguel", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2000, 12, 15), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 46, "pl_name": "Rui Pereira", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1995,  9, 17), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 47, "pl_name": "Daniel Pacheco", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1979,  8, 17), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 48, "pl_name": "Filipe Santos", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1996, 10,  6), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 49, "pl_name": "Rui Miguel Silva", 	  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1989,  9, 11), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 50, "pl_name": "Filipe Nascimento", 	  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1996, 10,  6), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 51, "pl_name": "Noé Oliveira", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1995,  9,  8), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 52, "pl_name": "Mario Garcia", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1984,  4,  2), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 53, "pl_name": "Bruno Miguel Ferreira", "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1979,  3, 22), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 54, "pl_name": "Bruno Silva", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1998,  8, 23), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 55, "pl_name": "Nuno Ferreira", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1988,  6, 21), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 56, "pl_name": "Ricardo Guimarães", 	  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1984,  7,  9), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 57, "pl_name": "Rita Correia", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1999,  1,  1), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 58, "pl_name": "Rafael Moreira", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2000,  3, 22), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 59, "pl_name": "Antônio Martins", 	  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2012,  5,  4), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 60, "pl_name": "João Ferreira", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1993,  8,  9), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 61, "pl_name": "Francisco Neto", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2000,  1, 29), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 62, "pl_name": "Duarte Pereira", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2010, 11, 23), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 63, "pl_name": "Tiago Silva Mascote",   "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1996,  9, 29), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1000, "pl_ranking_stat": "Y"},
            {"pl_id": 64, "pl_name": "Ricardo Filipe Silva",  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(2000,  4, 21), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"},
            {"pl_id": 65, "pl_name": "Helder Sousa", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1978,  1,  9), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 66, "pl_name": "Filipe Alves", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1978, 11,  5), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 1200, "pl_ranking_stat": "Y"},
            {"pl_id": 67, "pl_name": "Mara Sampaio", 		  "pl_acron":  None, "pl_email": "",      						"pl_pwd": None,  "pl_birthday": date(1979,  3, 22), "pl_type": None, 		"pl_sex": None, "pl_level_sex": None, "pl_level_mx": None, "pl_2024_ELO": 800,  "pl_ranking_stat": "Y"}
        ]

        for player_data in players_data:
            player = Players(**player_data)
            db.session.add(player)

        db.session.commit()
    players_data = Players.query.all()
    return render_template('players.html', user=current_user, players=players_data)


@views.route('/player_detail/<playerID>')
def player_detail(playerID):
    current_Player = Players.query.filter_by(pl_id=playerID).first()
    player_data = {
        "player_id": current_Player.pl_id,
        "player_name": current_Player.pl_name,
        "player_email": current_Player.pl_email,
        "player_birthday": current_Player.pl_birthday,
        "numGameDayWins": 3,
        "lastGamePlayed": "2024-01-02",
        "games_won": 50,
        "total_games": 100,
        "best_teammate_name": "Jane Doe",
        "best_teammate_win_percentage": 75.0,
        "best_teammate_total_games": 50,
        "worst_teammate_name": "Jane Doew",
        "worst_teammate_lost_percentage": 75.0,
        "worst_teammate_total_games": 50,
        "worst_nightmare_name": "Jane Doe",
        "worst_nightmare_lost_percentage": 75.0,
        "worst_nightmare_games": 50,
        "best_opponent_name": "Jane Doew",
        "best_opponent_victory_percentage": 75.0,
        "best_opponent_games": 50
    }
    return render_template("player_detail.html", user=current_user, player=player_data)   


@views.route('/display_user_image/<userID>')
def display_user_image(userID):
    filePath = str(os.path.abspath(os.path.dirname(__file__)))+'/static/photos/users/'+str(userID)+'/main.jpg'
    if os.path.isfile(filePath):
        return redirect(url_for('static', filename='photos/users/'+ str(userID)+'/main.jpg'), code=301)
    else:
        return redirect(url_for('static', filename='photos/users/nophoto.jpg'), code=301)


    