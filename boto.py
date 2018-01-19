"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request , response
from datetime import datetime, timedelta
import urllib, json
import random
import requests
import forecastio
import curselist

curses = curselist.curses



info = {
    "confirm_name" : False,
    "set_name" : False
}

intro = ["hi","hello","howdy"]
yes = ["yes","yeah","yup","y"]
no =["no","nope","n"]

@route('/', method='GET')
def index():
    return template("chatbot.html")

def check_been_before():
    visited = request.get_cookie("been")
    if visited:
        return True
    else:
        response.set_cookie(name="been", value= "visit" ,
        expires=datetime.now() + timedelta(days=30))

        return False

def random_animation():
    animations= ["afraid","bored","confused","crying","dancing","dog","excited","giggling",
    "heartbroke","involve","laughing","money","no","ok","takeoff","waiting"]

    return random.choice(animations)

def joke():
    url = "https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    setup = data["setup"]
    punchline= data["punchline"]
    return setup,punchline

def check_curse(msg):
    if any(word in msg for word in curses):
        return True

def get_weather():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']

    api_key = "e373ad12c7899f414c3be6eeb3467c1a"
    forecast = forecastio.load_forecast(api_key, lat, lon)
    return "The current temperature is {0} celcius outside".format(forecast.currently().temperature)


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    word_list = user_message.lower().split()

    been_before = check_been_before()
    animation = random_animation()

    name = request.get_cookie("name")

    if info['set_name']:
        response.set_cookie(name="name", value=user_message, expires=datetime.now() + timedelta(days=30))
        name = user_message
        info['set_name'] = False

        botresponse = "Your name is {0} , got it!".format(user_message)

        return json.dumps({"animation": animation, "msg": botresponse})

    # default response
    if name:
        botresponse ="{}, I didn't understand. Type in 'commands' to see what I can do. Bleep Bloop.".format(name)
    else:
        botresponse ="I didn't understand. Type in 'commands' to see what I can do. Bleep Bloop."


    if been_before == False:
        print "assign name"
        response.set_cookie(name="name", value= user_message,
        expires=datetime.now() + timedelta(days=30))
        info["confirm_name"] = True
        botresponse = "Okay, i think your name is {0}, so I will call you that from now on. Is {0} your name?".format(user_message)

        return json.dumps({"animation": animation, "msg": botresponse})



    if 'wubba lubba dub dub' in  user_message.lower():
        if name:
            botresponse = "{}, I can see you are in great pain. How may I assist you?".format(name)
        else:
            "I can see you are in great pain. How may I assist you?"

    if word_list[0] in intro:
        if name:
            botresponse = "{} ,I am boto the intelligent Pythonic Robot. Bleep Bloop.".format(name)
        else:
            botresponse = "I am boto the intelligent Pythonic Robot. Bleep Bloop."

    if '?' in user_message:
        if name:
            botresponse = "That's a great question, {} I don't know the answer though. Bleep Bloop".format(name)

    if any(word == 'weather' for word in word_list):
        botresponse = get_weather()

    if any(word == 'joke' for word in word_list):
        setup,punchline = joke()
        botresponse = setup + "......." +punchline
        animation = "laughing"

    if word_list[0] == 'commands' or word_list[0]=='command':
        botresponse="Try 'joke' for a hysterical joke. Try 'weather' to get the current temperature!"
        animation = "ok"

    if check_curse(user_message.lower()):
        botresponse = "Hey! No cursing! I am boto. Bleep Bloop."
        animation = "no"

    if info['confirm_name']:
        print "reached confirm name"
        if any(word in yes for word in word_list):
            botresponse = "That's what I thought!"
            info['confirm_name']=False
        else:
            botresponse = "What is your name? Just one word please."
            info['set_name']=True
            info['confirm_name']=False

    return json.dumps({"animation": animation, "msg": botresponse})



@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    run(host='localhost', port=7000)

if __name__ == '__main__':
    main()
