from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.dbjungle

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port = 5700, debug = True)