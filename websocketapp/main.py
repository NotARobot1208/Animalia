#!/usr/bin/env python3

import asyncio
import websockets
import json
import hashlib
import random
import uuid
import time

from questions import get_animal_question_mc
from db import User
from rating import get_new_ratings
from util import decode_cookie

class Player:
    def __init__(self, id, ws, score=0):
        self.id = id
        self.score = score
        self.wrong = 0
        self.answered = 0
        self.has_answered = False
        self.ws = ws
    def set_user(self):
        self.user = User(self.id)

class Game:
    def __init__(self, game_id, p1_id, p1_ws):
        self.problem = 0
        self.game_id = game_id
        self.players = {p1_id: Player(p1_id, p1_ws)}
        self.p1 = self.players[p1_id]
        self.p2 = None
        self.initiated = False
        self.current_question = ''
        self.current_answer = ''
        self.current_answer_choices = []
        self.accepting = False
        self.asked_questions = []
    async def next(self):
        if self.problem == 9:
            await self.end()
        else:
            self.accepting = False
            print("entered next")
            self.problem += 1
            correct = self.current_answer
            q = json.loads(get_animal_question_mc(self.asked_questions))["results"][0]
            self.current_question = q['question']
            self.asked_questions.append(q['question'])
            self.current_answer = q['correct_answer']
            self.current_answer_choices = q['incorrect_answers']
            self.current_answer_choices.append(q['correct_answer'])
            random.shuffle(self.current_answer_choices)
            for k in self.players.keys():
                if self.problem != 1:
                    await self.players[k].ws.send(json.dumps({"code": self.game_id, "message": f"Correct answer: {correct}"}))
                await self.players[k].ws.send(json.dumps({"code": self.game_id, "scores": {self.p1.user.username: self.p1.score, self.p2.user.username: self.p2.score}}))
        await asyncio.sleep(5)
        self.accepting = True
        print("sending questions")
        for k in self.players.keys(): # set up for next question
            await self.players[k].ws.send(json.dumps({"code": self.game_id, "problem": self.problem, "question": self.current_question, "answer_choices": self.current_answer_choices}))
            self.players[k].has_answered = False
    async def end(self):
        winner = ""
        user1 = User(self.p1.id)
        user2 = User(self.p2.id)
        if self.players[user1.id].score > self.players[user2.id].score:
            winner_uname = user1.username
            winner = "A"
        elif self.players[user1.id].score < self.players[user2.id].score:
            winner_uname = user2.username
            winner = "B"
        else:
            winner_uname = "Tie"
            winner = "T"
        user1.rating, user2.rating = get_new_ratings(user1.rating, user2.rating, winner)
        user1.correct_questions += self.p1.score
        user2.correct_questions += self.p2.score
        user1.questions += self.p1.answered
        user2.questions += self.p2.answered
        user1.update()
        user2.update()
        for k in self.players.keys(): # set up for next question
            await self.players[k].ws.send(json.dumps({"code": self.game_id, "winner": winner_uname, "ratings": {user1.username: user1.rating, user2.username: user2.rating}}))
            await self.players[k].ws.close()

games = {}
async def process(websocket):
    async for message in websocket:
        print(message)
        message = json.loads(message)
        if message['type'] == 'initiate':
            game_id = hashlib.sha256((str(uuid.uuid4()) + message['sid']).encode()).hexdigest()[:8]
            p1_id = decode_cookie(message['sid'])['_user_id'] # same ID as in database
            games[game_id] = Game(game_id, p1_id, websocket)
            games[game_id].players[p1_id].set_user()
            out = {"success": True, "gameid": game_id}
            await websocket.send(json.dumps(out))
        elif message['type'] == 'join':
            if len(games[message['code']].players.keys()) == 1:
                id = decode_cookie(message['sid'])['_user_id']
                if str(id) in games[message['code']].players.keys():
                    out = {"success": False, "error": "Cannot start a game with yourself."}
                    await websocket.send(json.dumps(out))
                else:
                    games[message['code']].players[str(id)] = Player(id, websocket)
                    games[message['code']].players[str(id)].set_user()
                    games[message['code']].p2 = games[message['code']].players[str(id)]
                    games[message['code']].initiated = True
                    await games[message['code']].next() # initiate challenge
            else:
                out = {"success": False, "error": "Game full."}
                await websocket.send(json.dumps(out))
        elif message['type'] == 'getquestion': # fetches question, shouldnt really be used
            out = {"code": message['code'], "question": games[message['code']].current_question, "answer_choices": games[message['code']].current_answer_choices}
            await websocket.send(json.dumps(out))
        elif message['type'] == 'answerquestion':
            id = decode_cookie(message['sid'])['_user_id']
            if games[message['code']].accepting == True:
                games[message['code']].players[id].answered += 1
                if games[message['code']].players[id].has_answered:
                    out = {"success": False, "error": "Too many attempts!"}
                else:
                    games[message['code']].players[id].has_answered = True
                    if message['answer'].lower() == games[message['code']].current_answer.lower():
                        games[message['code']].accepting = False
                        games[message['code']].players[id].score += 1
                        out = {"success": True, "correct": True}
                        await websocket.send(json.dumps(out))
                        for k in games[message['code']].players.keys():
                            if games[message['code']].players[k].id != id:
                                await games[message['code']].players[k].ws.send(json.dumps({"code": message['code'], "message": f"{games[message['code']].players[id].user.username} answered the question correctly!"}))
                        await games[message['code']].next()
                    else:
                        games[message['code']].players[id].wrong += 1
                        out = {"success": True, "correct": False}
                        await websocket.send(json.dumps(out))
                        for k in games[message['code']].players.keys():
                            if games[message['code']].players[k].id != id:
                                await games[message['code']].players[k].ws.send(json.dumps({"code": message['code'], "message": f"{games[message['code']].players[id].user.username} answered the question incorrectly."}))
                        if all([games[message['code']].players[n].has_answered for n in games[message['code']].players.keys()]):
                            games[message['code']].accepting = False
                            await games[message['code']].next()
            else:
                out = {"code": message['code'], "message": "Not accepting responses."}
                    
            
async def main():
    async with websockets.serve(process, "0.0.0.0", 80):
        await asyncio.Future()

asyncio.run(main())