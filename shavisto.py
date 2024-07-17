#!/bin/python3

import json
import time

import telebot

from transcribe import detect_ws, shavise, latinise


with open(f"/etc/shavisto/token.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    token = data["KeyAPI"]
    LATIN_ID = data["LatinID"]
    SHAVIAN_ID = data["ShavianID"]

with open("welcome.txt", "r", encoding="utf-8") as f:
    welcome = f.read().rstrip()

bot = telebot.TeleBot(token)

history = {}

def handle_text(text, cid):
    """ mirror groups and transcribe if asked """
    if cid == LATIN_ID:
        target_id = SHAVIAN_ID
        transcription = shavise(text)
    elif cid == SHAVIAN_ID:
        target_id = LATIN_ID
        transcription = latinise(text)
    else:
        target_id = cid
        ws = detect_ws(text)
        match ws:
            case "latin":
                transcription = shavise(text)
            case "shavian":
                transcription = latinise(text)
    return transcription, target_id

@bot.message_handler(commands=['start', 'help'])
def help(message):
    with open("logo.png", "rb") as f:
        bot.send_photo(message.from_user.id, f, caption=welcome)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """ track sent messages to transcribe them """
    global history
    # get all vars
    text = message.text
    cid = message.chat.id
    mid = message.message_id
    user = message.from_user.first_name
    # get transcription
    transcription, target_id = handle_text(text, cid)
    # respond
    response_text = f"{user}: {transcription}"
    while True:
        try:
            response = bot.send_message(target_id, response_text)
        except Exception:
            time.sleep(3)
            response = bot.send_message(target_id, response_text)
        break
    rid = response.message_id
    # record
    history[mid] = rid

@bot.edited_message_handler(func=lambda message: True)
def handle_edited_message(message):
    """ track changes to already transcribed messages to redact them """
    global history
    # get all vars
    text = message.text
    cid = message.chat.id
    mid = message.message_id
    user = message.from_user.first_name
    # get transcription
    transcription, target_id = handle_text(text, cid)
    # respond
    response_text = f"{user}: {transcription}"
    rid = history.get(mid, 0)
    if rid != 0:
        while True:
            try:
                bot.edit_message_text(response_text, target_id, rid)
                break
            except Exception:
                time.sleep(3)
                bot.edit_message_text(response_text, target_id, rid)

bot.infinity_polling()
