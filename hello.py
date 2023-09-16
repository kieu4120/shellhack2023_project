from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import threading
app = Flask(__name__)


#for openai API
import openai
openai.api_key = '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'
model_id = 'gpt-3.5-turbo'


@app.route('/functioning')
def functioning():
    cv = ChatGPT_conversation(selected_option)
    return jsonify({'status': 'Done'})
    

def ChatGPT_conversation(choice):

    #user prompts the input
   
    #user picks a category to generate a story.

    
    response =  openai.ChatCompletion.create(
        model=model_id,
        messages= [{'role':'user', 'content': f"Write a story with topic {choice}"}],
        max_tokens = 50,
        temperature = 0.6
    )

    #api output
    output = response["choices"][0]["message"]["content"]
    print(output)

    return output


@app.route('/', methods=['GET', 'POST'])
def index():
    print("cool")
    if request.method == 'POST':
        name = request.form.get('name')
        return redirect(url_for('hello', name=name))

    return render_template('index.html')

@app.route('/hello/<name>')
def hello(name):
    return render_template("hello.html", name=name)
  
@app.route('/menu', methods=['GET', 'POST'])
def menu():

    if request.method == 'POST':
        choice = request.form.get('choice')
        other_input = request.form.get('other_input')
        global selected_option
        if choice == "Other" and other_input:
            selected_option = other_input
            
        else:
            selected_option = choice
            
        return redirect(url_for('loading'))

        # return redirect(url_for('loading'))
    
    return render_template('menu.html')

is_finished = False




@app.route('/loading')
def loading():
    return render_template('loading.html')


    



@app.route('/result')
def result():
    return "Task completed! Here's the result."



if __name__ == '__main__':
    app.run(debug=True,port=8000)