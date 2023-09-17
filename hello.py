from flask import Flask, render_template, request, redirect, url_for, jsonify

#requests lib for TTS api
import requests, json, time

app = Flask(__name__)

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
@app.route('/', methods=['GET', 'POST'])
def index():
    print("cool")
    if request.method == 'POST':
        name = request.form.get('name')
        return redirect(url_for('hello', name=name))

    return render_template('index.html')

#after putting in names
@app.route('/hello/<name>')
def hello(name):
    return render_template("hello.html", name=name)
  

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
    return render_template("result.html")



if __name__ == '__main__':
    app.run(debug=True,port=8000)