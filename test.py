import hashlib
import datetime
import requests
import certifi
import jwt
SECRET_KEY = 'SPARTA'
from bs4 import BeautifulSoup
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)

ca = certifi.where()

client = MongoClient("mongodb+srv://test:sparta@atlascluster.e9m9dht.mongodb.net/Cluter0?retryWrites=true&w=majority", tlsCAFile=ca)
db = client.hotels

######################### 키값 세션#####################################################

##########################키 값 세션 끝 #################################################   
   
#######################로그인 세션  ####################################################

#############################로그인 세션 끝 #################################################

############################회원 가입 세션 ###################################################


####################회원 가입 세션 끝 #####################################################

######################index.html############################################################

@app.route('/index')
def home():
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
    
    print(imageUrl_receive, star_receive, desc_receive,hotelName_receive, local_receive)
    
    doc = {'url':imageUrl_receive, 
            'star':star_receive, 
            'desc':desc_receive, 
            'local':local_receive, 
            'hotelName': hotelName_receive
        }
    db.post.insert_one(doc)
    return jsonify ({'msg' : '등록 감사합니다.!'})

@app.route("/index/post", methods=["GET"])
def postbox_get():
    
    hotelsList = list(db.post.find({},{'_id':False}))

    return jsonify({'hotelsList':hotelsList})
 
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)