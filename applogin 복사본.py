from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
import certifi
import hashlib
import datetime
import jwt
SECRET_KEY = 'TEAM3'
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.abnjiys.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


##  HTML을 주는 부분  ##

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


# ##  로그인을 위한 API ##
# ## 회원가입 register.html ##

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


# ## 로그인 login.html ##
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
          payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
           }
          # token을 줍니다.
          token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
          return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


# postbox 작성 API ##
@app.route('/', methods=['POST'])
def postbox_post():
    url_receive = request.form('url_give')
    hotelName_receive = request.form['hotelName']
    image_receive = request.files('image')
    location_receive = request.form['location']
    latitude_receive = request.form['latitude']
    longitude_receive = request.form['longitude']
    local_receive = request.form['local']
    print(url_receive, hotelName_receive, image_receive, location_receive, latitude_receive, longitude_receive,
          local_receive)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('url_receive', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    for hotel in hotels:
        h = hotel.select_one('common_Header__LoN6F > div > strong')
        if h is not None:
            url = soup.select_one('meta[property="og:title"]')['content']
            hotelName = soup.select_one(
                'meta[property="og:image:alt"]')['content']
        image = soup.select_one('meta[property="og:image"]')['content']
        location = soup.select_one(
            'meta[property="og:street_address"]')['content']
        latitude = soup.select_one(
            'meta[property="location:latitude"]')['content']
        longitude = soup.select_one(
            'meta[property="location:longitude"]')['content']

        doc = {'url': url, 'hotelName': hotelName, 'image': image, 'location': location, 'latitude': latitude,
               'longitude': longitude, 'local': local_receive
               }
        print(doc)
        db.hotel.insert_one(doc)

        return jsonify({'msg': 'post success'})


## postcard 보기 API ##
@app.route('/postcard', methods=['GET'])
def postcard_get():
    hotel_list = list(db.hotel.find())
    return jsonify({'hotel_list': hotel_list})


## 리뷰작성페이지
@app.route('/reviewpage', methods=['POST'])
def reviewpage_post():
    url_receive = request.form('url_give')
    image_receive = request.files('image_give')
    local_receive = request.form['local_give']
    star_receive = request.form['star_give']
    user_receive = request.form['user_give']

    return jsonify({'msg': '리뷰완료'})


## comment 삭제 API ##
@app.route('/comment', methods=['DELETE'])
def commet_delete():
    comment_receive = request.form['comment_give']
    db.hotel.delete_one({'comment': comment_receive})
    return jsonify({'msg': '삭제완료'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)