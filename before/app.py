import jwt
import hashlib
import datetime
from flask import Flask, request, render_template, jsonify,url_for, redirect
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from time import time
import config

app = Flask(__name__)
# client = MongoClient(config.MONGO_DB, 27017)
client = MongoClient('localhost', 27017)
db = client.mate

SECRET_KEY = config.SECRET_KEY


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return redirect(url_for("main"))
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
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
    
    resultId=db.user.find_one({'id': id_receive})
    if resultId is None:
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        # pw_hash = request.form['pw_give']
        db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name':name_receive, 'class': class_recieve, 'my_board': [], 'my_join': []})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})
    

        
          #   중복확인 // find로 같은 아이디 있는 경우 Fail 보내고 else> success 보내기


@app.route('/main')
def main():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = payload['id']
    user = db.user.find_one({'id':user_info}, {'_id': False})
    print(user)

    img_logo = '../static/no_img.png'
    items = list(db.board.find({}, {'_id': False}).sort('time_exp',1))
    if not items :
        db.counter.update_one({'_id':'num'},{'$set':{'seq':0}}) 
    
    return render_template('main.html', items = items, img_logo = img_logo, user = user )
 

@app.route('/main', methods = ['POST'])
def post_item():
    counter = db.counters

    title =  request.form['title']
    content = request.form['content']
    item_link = request.form['item_link']
    chat_link = request.form['chat_link']
    time_exp = request.form['time_exp']
    expire_time = int((time() / 60) + (float(time_exp) * 60)) # 만료 기한 ( 분단위 )
    # creator 를 알아볼만한 정보가 필요함
    creator = request.form['user']
    min_people = request.form['min_people']
    cur_people = 1

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(item_link, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    og_image = soup.select_one('meta[property="og:image"]')
    url_image = og_image['content']
    num_give = counter.find_one_and_update(filter={"_id": "num"}, update={"$inc": {"seq": 1}}, new=True)["seq"]
    
    db.board.insert_one({'title':title, 'content':content, 'item_link':item_link,
                         'chat_link':chat_link, 'time_exp':expire_time, 'creator':creator,
                         'min_people':min_people, 'cur_people':cur_people,
                         'url_image':url_image, 'num' : num_give})
    # db.user.update_one({},{'$addToSet':{'my_board':num_give}})
    return jsonify({'result': 'success'})


# @app.route('/detail', methods=['GET'])
# def detail():
#         token_receive = request.cookies.get('mytoken')
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = payload['id']
        
#         num = request.args.get('num')
        
#         result = list(db.board.find({"num": int(num)}))
        
#         return render_template('detail.html', result=result, user_info = user_info)

@app.route('/detail', methods=['GET'])
def detail():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = payload['id']
    
    user = db.user.find_one({'id':user_info}, {'_id': False})
    
    num = request.args.get('num')
    
    result = list(db.board.find({"num": int(num)}))

    my_join_list = user['my_join']
    
    return render_template('detail.html', result=result,my_join_list = my_join_list, user_info = user_info)

      
@app.route('/detail',methods=['POST'])
def joinGroup():
    num_receive = request.form['num_give']
    print(num_receive)
    user_info = request.form['user_name']
    # print(user_info)
    user = db.user.find_one({'id':user_info}, {'_id': False})
    result = db.board.find_one({'num':int(num_receive)})
    if int(num_receive) not in user['my_join']:
        new_cur_people = result['cur_people']+1
        db.board.update_one({'num':int(num_receive)},{'$set':{'cur_people':new_cur_people}})
        db.user.find_one_and_update(filter={"id": user_info}, update={'$addToSet':{'my_join':int(num_receive)}})
    else:
        new_cur_people = result['cur_people']-1
        db.board.update_one({'num':int(num_receive)},{'$set':{'cur_people':new_cur_people}})
        db.user.find_one_and_update(filter={"id": user_info}, update={'$pull':{'my_join':int(num_receive)}})
    # user = db.user.find_one({'id':user_info}, {'_id': False})
    # user['my_join'].append(num_receive);
    # print(user['my_join'])
    # db.user.update_one({},{'$addToSet':{'my_join':int(num_receive)}})
    
    return jsonify({'result': 'success'})

# @app.route('/detail',methods=['POST'])
# def cancleGroup():
#     num_receive = request.form['num_give']
      
#     result = db.board.find_one({'num':int(num_receive)})
#     new_cur_people = result['cur_people']-1
    
#     db.board.update_one({'num':int(num_receive)},{'$set':{'cur_people':new_cur_people}}) 
       
    
#     return jsonify({'result': 'success'})
  
    
if __name__ == '__main__':
    app.run('0.0.0.0', port = 5600, debug = True)