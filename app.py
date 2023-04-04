from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.mate

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/main')
def main():
    title = "솔트레인 치약 6입"
    content = "세명 모여서 두 개씩 나눠서 쓰면 좋을 것 같아요. 6개에 40,000원, 인당 13,000원(제가 천원 더 낼게요)"
    item_link = "https://www.naver.com/"
    chat_link = "https://www.coupang.com"
    time_exp = "13:00"
    creator = "bigperson"
    min_people = 3
    cur_people = 1
    # items = list(db.board.find({}, {'_id': False}).sort('time', -1))

    return render_template('main.html', 
                           title = title, content = content, 
                           item_link = item_link, chat_link = chat_link, 
                           time_exp = time_exp, creator =creator, 
                           min_people = min_people, cur_people = cur_people )


@app.route('/main', methods = ['POST'])
def post_item():
    title =  request.form['title']
    content = request.form['content']
    item_link = request.form['item_link']
    chat_link = request.form['chat_link']
    time_exp = request.form['time_exp']
    # creator 를 알아볼만한 정보가 필요함
    creator = "bigperson"
    min_people = request.form['min_people']
    cur_people = 1
    db.board.insert_one({'title':title, 'content':content, 'item_link':item_link,
                         'chat_link':chat_link, 'time_exp':time_exp, 'creator':'bigperson',
                         'min_people':min_people, 'cur_people':1})
    return jsonify({'result': 'success'})


@app.route('/detail')
def detail():
    return render_template('detail.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port = 5700, debug = True)