from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import threading
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
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
        if choice == "Other" and other_input:
            selected_option = other_input
        else:
            selected_option = choice
        return redirect(url_for('loading'))
    
    return render_template('menu.html')

is_finished = False
def simulate_long_running_task():
    time.sleep(5)  # Simulate a 5-second delay (replace with your actual task)
    is_finished = True



@app.route('/loading')
def loading():
    if is_finished == False:
        background_thread = threading.Thread(target=simulate_long_running_task)
        background_thread.start()
        
        # Wait for the task to finish (you can use more sophisticated methods)
        background_thread.join()
   
    # Redirect to a different route after the task is done
        return redirect(url_for('result'))
    return render_template('loading.html')



@app.route('/result')
def result():
    return "Task completed! Here's the result."



if __name__ == '__main__':
    app.run(debug=True)