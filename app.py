from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from simulation import simulate
from paths import img_path
import os
import atexit

# TODO: 404 page, deploy somewhere

scheduler = BackgroundScheduler()
scheduler.add_job(func=simulate, trigger="interval", seconds=5)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

@app.route('/', methods=['GET','POST'])
def index():
    if simulation_started():
        return render_template('index.html')
    return render_template("sorry.html")

@app.route('/about')
def about():
    if simulation_started():
        return render_template('about.html')
    return render_template("sorry.html")

@app.route('/ranking')
def ranking():
    if simulation_started():
        return render_template('ranking.html')
    return render_template("sorry.html")

@app.route('/res')
def res():
    return render_template('res.html')

@app.route('/scores')
def scores():
    return render_template('scores.html')


def simulation_started():
    return os.path.exists(img_path)


if __name__ == '__main__':
    app.run(debug=True)
