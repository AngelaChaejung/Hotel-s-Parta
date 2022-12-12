from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.8q7d5by.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def home():
   return render_template('index.html')

@app.route("/hotel", methods=["POST"])
def movie_post():

    name_receive = request.form['name_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    doc = {
        'name':name_receive,
        'star':star_receive,
        'comment':comment_receive
    }

    db.hotel.insert_one(doc)

    return jsonify({'msg':'저장 완료!'})

@app.route("/hotel", methods=["GET"])
def movie_get():
    hotel_list = list(db.hotel.find({},{'_id':False}))
    return jsonify({'hotel':hotel_list})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)