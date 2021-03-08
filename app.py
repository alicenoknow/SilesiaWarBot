from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from simulation import simulate
import atexit

scheduler = BackgroundScheduler()
scheduler.add_job(func=simulate, trigger="interval", minutes=1)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/ranking')
def ranking():
    return render_template('ranking.html')

@app.route('/res')
def res():
    return render_template('res.html')

@app.route('/scores')
def scores():
    return render_template('scores.html')


if __name__ == '__main__':
    app.run()
