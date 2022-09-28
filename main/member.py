from main import *
from flask import Blueprint

bp = Blueprint("member", __name__, url_prefix="/member")

# 회원가입
@bp.route("/join", methods=("GET", "POST"))
def member_join():
    if request.method == "POST":
        name = request.form.get('name', type=str)
        email = request.form.get('email', type=str)
        pass1 = request.form.get('pass', type=str)
        pass2 = request.form.get('pass2', type=str)        

        if name == "" or email == "" or pass1 == "" or pass2 == "":
            flash('입력되지 않은 값이 있습니다')
            return render_template('join.html', title='회원가입')
        if pass1 != pass2:
            flash('비밀번호가 일치 하지 않습니다')
            return render_template("join.html", title='회원가입')
                
        # 아이디 중복검사
        members = mongo.db.members
        cnt = members.count_documents({"email": email})
        if cnt > 0:
            flash("중복된 이메일 주소입니다")
            return render_template('join.html', title='회원가입')
                    
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
        return render_template("join.html", title='회원가입')


# 회원로그인
@bp.route("/login", methods=("GET", "POST"))
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
            return redirect(url_for("member.member_login"))
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
                    return redirect(url_for("board.lists"))
                
            else:
                flash('비밀번호가 일치 하지 않습니다')
                return redirect(url_for("member.member_login"))           
        return ''
    else:
        # get
        next_url = request.args.get("next_url", type=str)
        print(f'next_url : {next_url}')
        if next_url is not None:
            return render_template('login.html', next_url=next_url, title='로그인')
        else:
            return render_template("login.html", title='로그인')
        
# 로그아웃
@bp.route("/logout")
def member_logout():    
    try:
        del session['email']
        del session['name']
        del session['id']
    except:
        pass
    return redirect(url_for("board.lists", title='게시판리스트'))
 