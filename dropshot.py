#!/usr/bin/env python
from bottle import request, route, get, post, run, template
from sqlalchemy import or_
import models
import time

# ---- GET REQUESTS -----------------------------------------------------------

@get('/')
def home():
    return "dropshot is online"

@get('/ping')
def pong():
    return "pong"

@get('/players')
def get_players():
    input_count = int(request.query.get('count') or 100)
    input_offset = int(request.query.get('offset') or 0)
    
    playersQuery = models.session.query(models.Player).slice(input_offset, input_offset + input_count)
    playersAsJson = map(lambda player: player.to_dictionary(), playersQuery)

    return { 'count' : len(playersAsJson), 'offset' : input_offset, 'players' : playersAsJson }

@get('/players/<username>')
def get_player_by_username(username):
    playerQuery = models.session.query(models.Player).filter(models.Player.username == username)
    if (playerQuery.count() == 0):
        return { 'error' : 'no player found' }
    player = playerQuery.first()
    return player.to_dictionary()

@get('/players/<username>/games')
def get_games_by_username(username):
    return template('No games associated with player <b>{{username}}</b>.', username=username)

@get('/games/<game_id>')
def get_game_by_id(game_id):
    gameQuery = models.session.query(models.Game).filter(models.Game.id == gameId)
    if(gameQuery.count() == 0):
        return { 'error' : 'CANTFINDGAME' }
    game = gameQuery.first()
    return game.to_dictionary()

@get('/games')
def get_games():
    input_count = int(request.query.get('count') or 100)
    input_offset = int(request.query.get('offset') or 0)
    
    gamesQuery = models.session.query(models.Game).slice(input_offset, input_offset + input_count)
    gamesAsJson = map(lambda game: game.to_dictionary(), gamesQuery)

    return { 'count' : len(gamesAsJson), 'offset' : input_offset, 'games' : gamesAsJson }

@get('/logout')
def logout():
    return "Cannot logout."

# ---- POST REQUESTS ----------------------------------------------------------

@post('/games')
def post_games():
    input_winner = request.forms.get('winner')
    input_loser = request.forms.get('loser')
    input_winner_score = request.forms.get('winnerScore')
    input_loser_score = request.forms.get('loserScore')
    
    if( not (input_winner_score.isdigit() and input_loser_score.isdigit())):
        return "Cannot create game. Invalid scores"

    winnerQuery = models.session.query(models.Player).filter(models.Player.username == input_winner)
    loserQuery = models.session.query(models.Player).filter(models.Player.username == input_loser)

    if( not (winnerQuery.count() == 1 and loserQuery.count() == 1)):
        return "Cannot create game. Invalid players"

    winner = winnerQuery.one()
    loser = loserQuery.one()

    game = models.Game(winner=winner, loser=loser, winner_score=input_winner_score, loser_score=input_loser_score, timestamp=int(time.time()))
    models.session.add(game)
    models.session.commit()
    
    return game.to_dictionary()

@post('/players')
def post_players():
    input_username = request.forms.get('username')
    input_password = request.forms.get('password')
    input_email = request.forms.get('email')

    playerQuery = models.session.query(models.Player).filter(or_(models.Player.username == input_username, models.Player.email == input_email))
    if (playerQuery.count() > 0):
        return { 'error' : 'USEREXISTS' }

    player = models.Player(username = input_username, password = input_password, email = input_email)
    models.session.add(player)
    models.session.commit()

@post('/login')
def login():
    return "Cannot login."

#@route('/db')
#def create_db():
#    return models.session.query(models.Player).all()[0].to_json()

if __name__ == '__main__':
    run(host='localhost', port='3000')
