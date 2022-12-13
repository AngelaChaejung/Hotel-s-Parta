import hashlib
import datetime
import requests
import certifi
from pprint import pprint
import jwt
SECRET_KEY = 'team3'
from flask import session
from bs4 import BeautifulSoup
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

ca = certifi.where()

client = MongoClient("mongodb+srv://test:sparta@atlascluster.e9m9dht.mongodb.net/Cluster0?retryWrites=true&w=majority",
                     tlsCAFile=ca)
db = client.hotels


######################### 키값 세션#####################################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        ## 토큰 존재시 > index  없으면 > login으로 ##
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/logout')
def log_out():
    session.clear()
    ## 쿠키 삭제 후 통신 ##
    ## a.jax에서 쿠키 삭제 ##

    return redirect(url_for('/index/login'))


##########################키 값 세션 끝 #################################################

#######################로그인 세션  ####################################################
@app.route('/index/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/index/login', methods=['POST'])
def index_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#############################로그인 세션 끝 #################################################
@app.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect('/')

############################로그아웃 세션 #########################
###############################################################
############################회원 가입 세션 ###################################################
@app.route('/index/register', methods=['POST'])
def index_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one(
        {'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


@app.route('/register')
def register():
    return render_template('register.html')


####################회원 가입 세션 끝 #####################################################

######################index.html############################################################

@app.route('/index')
def index():
    # token_receive = request.cookies.get('mytoken')
    #     ## 토큰 존재시 > index  없으면 > login으로 ##
    #    if token_receive === null
    #        return render_template ('/index/login')
    ## 토큰 유무에 따라 접속 가능여부 확인 if elsr 검색 ##
    return render_template('index.html')


##################### index.html #######################################################

#################### postbox.html ########################################################

@app.route('/index/post', methods=['POST'])
def postbox_listing():
    imageUrl_receive = request.form['imageUrl_give']
    star_receive = request.form['star_give']
    desc_receive = request.form['desc_give']
    hotelName_receive = request.form['hotelName_give']
    local_receive = request.form['local_give']

    print(imageUrl_receive, star_receive, desc_receive, hotelName_receive, local_receive)

    doc = {'url': imageUrl_receive,
           'star': star_receive,
           'desc': desc_receive,
           'local': local_receive,
           'hotelName': hotelName_receive
           }
    db.post.insert_one(doc)
    return jsonify({'msg': '등록 감사합니다.!'})


@app.route("/index/post", methods=["GET"])
def postbox_get():
    hotelsList = list(db.post.find({}, {'_id': False}))

    return jsonify({'hotelsList': hotelsList})


#####################################포스트 카테고리 #########################################
#####################################서울 ###################################################
@app.route('/seoul', methods=['GET'])
def seoul_get():
    seoul = list(db.post.find({'local': '서울'}, {'_id': False}))
    return jsonify({'seoul': seoul})


@app.route('/chungcheong', methods=['GET'])
def chungcheong_get():
    chungcheong = list(db.post.find({'local': '충청'}, {'_id': False}))
    return jsonify({'chungcheong': chungcheong})


@app.route('/pusan', methods=['GET'])
def pusan_get():
    pusan = list(db.post.find({'local': '부산'}, {'_id': False}))
    return jsonify({'pusan': pusan})


@app.route('/gangwon', methods=['GET'])
def gangwon_get():
    gangwon = list(db.post.find({'local': '강원'}, {'_id': False}))
    return jsonify({'gangwon': gangwon})


@app.route('/jeju', methods=['GET'])
def jeju_get():
    jeju = list(db.post.find({'local': '제주'}, {'_id': False}))
    return jsonify({'jeju': jeju})


###################################리뷰포스트 페이지 ##########################################3
@app.route('/reviewpost')
def reviewpost():
    return render_template('reviewpost.html')

#@app.route('/review/<hotelName>', methods=['GET'])
#def reviewpage(hotelName):
#    hotelName_receive = request.args.get(hotelName)
#    info = list(db.post.find({'hotelName':hotelName_receive},{'_id':False}))
#    return jsonify({'info':info})

@app.route("/hotel", methods=["POST"])
def movie_post():
    name_receive = request.form['name_give']
    star_receive = request.form['star_give']
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    doc = {
        'name': name_receive,
        'star': star_receive,
        'comment': comment_receive,
        'url': url_receive
    }

    db.hotel.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})

@app.route("/hotel", methods=["GET"])
def movie_get():
    hotel_list = list(db.hotel.find({}, {'_id': False}))
    return jsonify({'hotel': hotel_list})
#############################################################################################


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
