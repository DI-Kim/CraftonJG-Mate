from flask import Flask, request, render_template, jsonify,url_for
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests

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
    img_logo = '../static/no_img.png'
    items = list(db.board.find({}, {'_id': False}))
    if not items :
       db.board.update_one({'_id':'num'},{'$set':{'seq':0}})
    
    return render_template('main.html', items = items, img_logo = img_logo )


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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(item_link, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    og_image = soup.select_one('meta[property="og:image"]')
    if url_image is not None:
        url_image = og_image['content']
    else:
        url_image = None

    db.board.insert_one({'title':title, 'content':content, 'item_link':item_link,
                         'chat_link':chat_link, 'time_exp':time_exp, 'creator':'bigperson',
                         'min_people':min_people, 'cur_people':cur_people,
                         'url_image':url_image, 'board_id' : db.board.find_one_and_update(filter={"_id": "num"}, update={"$inc": {"seq": 1}}, new=True)["seq"]})
    return jsonify({'result': 'success'})


@app.route('/detail')
def detail():
    
    
    return render_template('detail.html')

@app.route('/detail', methods=['POST'])
def show_detail():
    title = request.form['title']
    
    result = db.collection.find({"title":title})
    
    return render_template('detail.html',detail_data=result)

if __name__ == '__main__':
    app.run('0.0.0.0', port = 5600, debug = True)