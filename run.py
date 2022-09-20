from flask import Flask, request, render_template, url_for, jsonify, redirect, abort
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import time
import math


app = Flask(__name__)
app.config["MONGO_URI"] =  "mongodb://localhost:27017/myweb"
mongo = PyMongo(app)    # mongo 가 myweb을 가르킴


@app.template_filter("formatdatetime")
def format_datetime(value):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    
    value = datetime.fromtimestamp(int(value) / 1000) + offset
    return value.strftime("%Y-%m-%d %H:%M:%S")

@app.route("/list")    
def lists():
    keyword = request.args.get("keyword", '', type=str)
    search = request.args.get("search", -1, type=int)
    
    # 최종적으로 완성된 쿼리를 만들 변수(검색조건)
    query = {}
    # 실제 검색조건 $or, $and 는 리스트로 조건 줄수 있거덩
    search_list = []

    if search == 0:
        search_list.append({"title":{"$regex": keyword}})
    if search == 1:
        search_list.append({"contents": {"$regex" :keyword}})
    if search == 2:
        search_list.append({"title": {"$regex": keyword}})
        search_list.append({"contents":{"$regex": keyword}})
    if search == 3:
        search_list.append({"name": {"$regex": keyword}})
    
    if len(search_list) > 0:
        query = {"$or": search_list}  
        
    board = mongo.db.board        
    
    # 현재 페이지 위치 값 ( 값이 없는 경우 1page)
    page = request.args.get('page', 1, type=int)
    # 한 페이지당 게시물 출력 개수 == limit이 block 사이즈네
    limit = request.args.get("limit", 10, type=int)
    # 게시물 전체 개수
    tot_count = board.count_documents({})
    # 마지막 페이지 number
    last_page_num = math.ceil(tot_count / limit)
    # 블럭 사이즈 : 계산위한 기준값
    block_size = 5
    # 현재 블럭의 위치 
    #! block_start 계산을 위해 구한 값
    #! 남박사님 page가 1이면 > 0 준다 > 이래야 블럭 시작위치 구하기 편함
    block_num = int((page - 1) / block_size)            
    # 블럭 시작 위치 - 반복문사용 등
    block_start = int((block_num * block_size) + 1)
    # 블럭 끝 위치
    block_last = math.ceil(block_start + block_size - 1)
    
    # datas가 있어야지 html이동
    if board.count_documents({}) > 0:       
        datas = board.find(query).sort([("pubdate", -1)]).skip((page-1) * limit).limit(limit)
        return render_template(
            'list.html',             
            datas=datas,
            page=page,
            limit=limit,
            last_page_num=last_page_num,
            block_start=block_start,
            block_last=block_last,
            search=search,
            keyword=keyword
                               )
    else:
        print('datas가 없음')
        #? flash 메세지
        #? write.html 도 바꿔
        return render_template("list_not_data.html")

@app.route("/view/<idx>")
def board_view(idx):
    '''
        idx값을 받아서, mongodb에서 idx에 해당하는 값을 가져옴
    '''  
    # idx = request.args.get('idx')
    if idx is not None:
        
        page = request.args.get("page", type=int)
        print(f'view: page : {page}')
        
        search = request.args.get('search')
        keyword = request.args.get("keyword")
    
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})

        if data is not None:
            result = {
                "id": data.get('_id'),
                "name": data.get('name'),
                'title': data.get('title'),
                'contents': data.get('contents'),
                'pubdate': data.get('pubdate'),
                'view': data.get('view')
            }
            return render_template('view.html', result=result, data=data, page=page, search=search, keyword=keyword)

    else:
        return abort(404)

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
        # return redirect(url_for("board_view", idx=x.inserted_id))
        return redirect(url_for("board_view", idx=x.inserted_id))
    else:
        return render_template("write.html")
    
    
@app.route("/board_delete")
def board_delete():
    return ''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)