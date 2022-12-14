from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.8q7d5by.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

@app.route('/')
def home():
    return render_template('index.html')


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
