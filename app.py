from flask import *
from pymongo import MongoClient
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies, create_refresh_token)
import jwt
import hashlib
import datetime
from http import HTTPStatus


app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.mate

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return redirect(url_for("main", name=user_info["name"]))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def loginhome():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    resultId = db.user.find_one({'id': id_receive})
    resultPw = db.user.find_one({'pw': pw_hash})
    result = db.user.find_one({'id': id_receive, 'name': pw_hash})
    if resultId is None:
        return jsonify({'result': 'fail'})
    elif resultPw is None:
        return jsonify({'result': 'fail'})
    else :
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)    #언제까지 유효한지
        }
#         # #jwt를 암호화
#         # # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # token을 줍니다.   
#             return jsonify({'result': 'success'})
        return jsonify({'result': 'success','token':token})

@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/join',methods=['POST'])
def join_a():
    id_receive = request.form['id_give']
    name_receive = request.form['name_give']
    class_recieve = request.form['class_give']
    pw_receive = request.form['pw_give']
    
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # pw_hash = request.form['pw_give']
    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name':name_receive, 'class': class_recieve})
    
    return jsonify({'result': 'success'})
        #   #   중복확인 // find로 같은 아이디 있는 경우 Fail 보내고 else> success 보내기


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