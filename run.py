from flask import Flask, request, render_template, url_for, jsonify, redirect, abort, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import time
import math
from functools import wraps
from datetime import timedelta



app = Flask(__name__)
app.config["MONGO_URI"] =  "mongodb://localhost:27017/myweb"
mongo = PyMongo(app)    # mongo 가 myweb을 가르킴
app.config['SECRET_KEY'] = "gahoo11sdf1"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id') is None:
            return redirect(url_for('member_login', next_url=request.url))
        return f(*args, **kwargs)   #* 리턴으로 함수를 인자 넣어줘 줘야하는듯
    return decorated_function         


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
@login_required
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
        # data = board.find_one({"_id": ObjectId(idx)})
        data = board.find_one_and_update({"_id": ObjectId(idx)}, {"$inc":{"view": 1}}, return_document=True)

        if data is not None:
            result = {
                "id": data.get('_id'),
                "name": data.get('name'),
                'title': data.get('title'),
                'contents': data.get('contents'),
                'pubdate': data.get('pubdate'),
                'view': data.get('view'),
                "writer_id": session.get("id", "")
            }
            return render_template('view.html', result=result, data=data, page=page, search=search, keyword=keyword)

    else:
        return abort(404)


@app.route("/write", methods=["GET", "POST"])
@login_required
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
            "writer_id": session.get("id"),
            "view": 0            
        }
        x = board.insert_one(post)        

        # x.inserted_id >> ObjectId 자료형        
        # return redirect(url_for("board_view", idx=x.inserted_id))
        return redirect(url_for("board_view", idx=x.inserted_id))
    else:
        return render_template("write.html")
    
    
@app.route("/delete/<idx>")
def board_delete(idx):
    
    return ''

@app.route("/edit/<idx>", methods=("GET", "POST"))
def board_edit(idx):
    if request.method == "GET":
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if data is None:
            flash("해당 게시물이 존재 하지 않습니다")
            return redirect(url_for('lists'))
        else:
            if session.get('id') == data.get('writer_id'):
                # 이제 수정진행이지 : 로긴한사
                return render_template("edit.html", data=data)
            else:
                flash("글 수정 권한이 없습니다")
                return redirect(url_for('lists'))
    else:
        title = request.form.get('title', type=str)
        contents = request.form.get('contents', type=str)
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if data is None:
            flash('해당 게시물이 존재 하지 않습니다')
            return redirect(url_for('lists'))
        else:
            if session.get('id') == data.get('writer_id'):
                board.update_one({"_id": ObjectId(idx)}, {
                    "$set": {
                        "title": title,
                        "contents": contents
                    }
                })
                flash('수정되었습니다.')
                return redirect(url_for("board_view", idx=idx))
            else:
                flash('수정권한이 없습니다')
                return redirect(url_for("lists"))
        

# 회원가입
@app.route("/join", methods=("GET", "POST"))
def member_join():
    if request.method == "POST":
        name = request.form.get('name', type=str)
        email = request.form.get('email', type=str)
        pass1 = request.form.get('pass', type=str)
        pass2 = request.form.get('pass2', type=str)        

        if name == "" or email == "" or pass1 == "" or pass2 == "":
            flash('입력되지 않은 값이 있습니다')
            return render_template('join.html')
        if pass1 != pass2:
            flash('비밀번호가 일치 하지 않습니다')
            return render_template("join.html")
        
        # 아이디 중복검사
        members = mongo.db.members
        cnt = members.count_documents({"email": email})
        if cnt > 0:
            flash("중복된 이메일 주소입니다")
            return render_template('join.html')
                    
        # 삽입
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        post = {
            "name": name,
            "email": email,
            "pass": pass1,
            "joindate": current_utc_time,
            "logintime": "",
            "logincount": 0
        }
        members.insert_one(post)
        
        return ""
    else:
        return render_template("join.html")


# 회원로그인
@app.route("/login", methods=("GET", "POST"))
def member_login():
    if request.method == "POST":
        email = request.form.get('email', type=str)
        password = request.form.get("pass", type=str)
        next_url = request.form.get("next_url", type=str)

        #? 왜 "" 값인지 체크 안하냐
        
        members = mongo.db.members
        data = members.find_one({"email": email})
        if data is None:
            flash("회원 정보가 없습니다")
            return redirect(url_for("member_login"))
        else:   
            # 로그인하고, 세션 만들고
            if password == data.get("pass"):
                session["email"] = email
                session['name'] = data.get('name')
                session['id'] = str(data.get('_id'))
                    # str 로 줄수잇는거였으? 그럼 뭐하러 ObjectId 를 사용해
                session.permanent = True
                    # session 유지 시간을 컨트롤 하기 위해 True
                
                if next_url is not None:
                    return redirect(next_url)   #! 꼭 url_for 안해도됨>> 특정주소로 넘겨도됨
                else:
                    return redirect(url_for("lists"))
                
            else:
                flash('비밀번호가 일치 하지 않습니다')
                return redirect(url_for("member_login"))           
        return ''
    else:
        # get
        next_url = request.args.get("next_url", type=str)
        print(f'next_url : {next_url}')
        if next_url is not None:
            return render_template('login.html', next_url=next_url)
        else:
            return render_template("login.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)