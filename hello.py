from flask import Flask, render_template, request, redirect, url_for, jsonify

#for auth0
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


#requests lib for TTS api
import requests, json, time

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

#for openai API
import openai
openai.api_key = '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'
model_id = 'gpt-3.5-turbo'


#key for text to speech
apikey = "c50dcb69bamshe0261669095ecbbp1aa5f1jsnb6671c12abb7"

#headers for TTS API
headers = {'content-type': "application/json", 'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com", 'x-rapidapi-key': apikey}

@app.route('/functioning')
def functioning():
    global text
    text = ChatGPT_conversation(selected_option)

    #if lang_choice is english use TTS for eng
    if selected_language == 'en':
     TTS(text)
    #use TTS for es
    else:
        url = f"http://api.voicerss.org/?key=b1dd2a39ac07454799c3be2b70e6c844&hl=es-es&src={text}&r=-4"
        response = requests.post(url)

        with open("static/audio/audio.wav", 'wb') as f:
            f.write(response.content)

    return jsonify({'status': 'Done'})
    
#Helper function for openAI and TTS API
def ChatGPT_conversation(choice):
    # Decide which language to generate
    if selected_language =='en':
        prompt= f"Write a story with topic {choice}"
    else:
        prompt = f"Write a story with topic {choice} in Spanish."
    
    response =  openai.ChatCompletion.create(
        model=model_id,
        messages= [{'role':'user', 'content': prompt}],

        #token limits
        max_tokens = 50,
        temperature = 0.7
    )

    #OpenAi API output. - text
    output = response["choices"][0]["message"]["content"]
    print(output)
    return output


def TTS(output):
    #TTS API
    response = requests.request("POST", "https://large-text-to-speech.p.rapidapi.com/tts", data=json.dumps({"text": output}), headers=headers)
    id = json.loads(response.text)['id']
    eta = json.loads(response.text)['eta']
    #print(f'Waiting {eta} seconds for the job to finish...')
    #time.sleep(eta)
    response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
    while "url" not in json.loads(response.text):
        response = requests.request("GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
        print(f'Waiting some more...')
        time.sleep(3)
    
    #get URL from the API response to download soundbytes
    url = json.loads(response.text)['url']

    #
    response = requests.request("GET", url)
    filename = "static/audio/audio.wav"
    with open(filename, 'wb') as f:
        f.write(response.content)
    

    #TTS API.
    #print(output)

    return 
#main route
#@app.route('/', methods=['GET', 'POST'])
@app.route("/")
def home():
    return render_template(
        "base1.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )
    # if request.method == 'POST':
    #     name = request.form.get('name')
    #     return redirect(url_for('hello', name=name))

    # return render_template('index.html')


#call back to the login page?
#saving the session for the user, 
#so when they visit again; they dont have to sign back. 
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/hello")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

#clear user session in app and redirect to make sure the section is clear.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )



#after putting in names
@app.route('/hello')
def hello():
    return render_template(
        "hello.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )
    #return render_template("hello.html")
  

@app.route('/menu', methods=['GET', 'POST'])
def menu():

    if request.method == 'POST':
        global selected_language
        selected_language = request.form.get('selected_language')
        choice = request.form.get('choice')
        other_input = request.form.get('other_input')
        global selected_option
        if other_input:
            selected_option = other_input
        else:
            selected_option = choice
        print(selected_option)  
        return redirect(url_for('loading'))

    
    return render_template('menu.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.route('/result')
def result():
    return render_template("result.html", text=text)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))