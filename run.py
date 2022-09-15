from flask import Flask, request, render_template, url_for, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime


app = Flask(__name__)
app.config["MONGO_URI"] =  "mongodb://localhost:27017/myweb"
mongo = PyMongo(app)    # mongo 가 myweb을 가르킴

@app.route("/write", methods=["GET", "POST"])
def board_write():
    if request.method == "POST":
        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")
        
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        
        board = mongo.db.board 
        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "pubdate": current_utc_time,
            "view": 0
        }
        x = board.insert_one(post)        

        # x.inserted_id >> ObjectId 자료형        
        return str(x.inserted_id)
    else:
        return render_template("write.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)