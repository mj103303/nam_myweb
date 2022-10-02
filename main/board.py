from msvcrt import kbhit
from string import ascii_lowercase
from main import *
from flask import Blueprint
import random
from flask import send_from_directory

bp = Blueprint("board", __name__, url_prefix="/board")

def board_delete_attach_file(filename):
    abs_path = os.path.join(app.config['BOARD_ATTACH_FILE_PATH'], filename)
    if os.path.exists(abs_path):    # 파일이 존재해야지 삭제하지
        os.remove(abs_path)
        return True
    return False


# 에이잭스 테스트
@bp.route("/ajax")
def ajaxtest():
    return render_template("test.html")

@bp.route("/test")
def test():
    return "AJAX CALL 111"

# image를 저장만함 ,url 리턴 안함
@bp.route("/upload_image", methods=("POST",))
def upload_image():
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename ='{}.jpg'.format(rand_generate())  # 8자 랜덤한 문자
        savefilepath = os.path.join(app.config['BOARD_IMAGE_PATH'], filename)
        file.save(savefilepath)
        return url_for('board.board_images', filename=filename)
    
# image file 리턴 - 아 요건 게시판 이미지 업로드하고 상관없네 >> 아미지 다운로드 할때 사용
@bp.route("/images/<filename>")
def board_images(filename):
    return send_from_directory(app.config['BOARD_IMAGE_PATH'], filename)

@bp.route("/files/<filename>")
def board_files(filename):
    return send_from_directory(app.config['BOARD_ATTACH_FILE_PATH'], filename, as_attachment=True)
    

@bp.route("/list")
def lists():
    keyword = request.args.get("keyword", '', type=str)
    search = request.args.get("search", -1, type=int)

    # 최종적으로 완성된 쿼리를 만들 변수(검색조건)
    query = {}
    # 실제 검색조건 $or, $and 는 리스트로 조건 줄수 있거덩
    search_list = []

    if search == 0:
        search_list.append({"title": {"$regex": keyword}})
    if search == 1:
        search_list.append({"contents": {"$regex": keyword}})
    if search == 2:
        search_list.append({"title": {"$regex": keyword}})
        search_list.append({"contents": {"$regex": keyword}})
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
        datas = board.find(query).sort(
            [("pubdate", -1)]).skip((page-1) * limit).limit(limit)
        return render_template(
            'list.html',
            datas=datas,
            page=page,
            limit=limit,
            last_page_num=last_page_num,
            block_start=block_start,
            block_last=block_last,
            search=search,
            keyword=keyword,
            title='게시판 리스트'
        )
    else:
        print('datas가 없음')
        #? flash 메세지
        #? write.html 도 바꿔
        return render_template("list_not_data.html", title='오류페이지')

# 글상세
@bp.route("/view/<idx>")
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
        data = board.find_one_and_update({"_id": ObjectId(idx)}, {
                                         "$inc": {"view": 1}}, return_document=True)

        if data is not None:
            result = {
                "id": data.get('_id'),
                "name": data.get('name'),
                'title': data.get('title'),
                'contents': data.get('contents'),
                'pubdate': data.get('pubdate'),
                'view': data.get('view'),
                "writer_id": session.get("id", ""),
                # 파일업로드 추가내용
                "attachfile": data.get('attachfile', '')
                # 파일업로드 추가내용 end
            }
            return render_template('view.html', result=result, data=data, page=page, search=search, keyword=keyword, title="상세보기")
    else:
        return abort(404)


@bp.route("/write", methods=["GET", "POST"])
@login_required
def board_write():
    if request.method == "POST":
        # 추가코드1
        filename = None
        if 'attachfile' in request.files:   # attachfile 있는지 확인 (html의 name 값)
            # request.files 하면 
            file = request.files['attachfile']
            if file and allowed_file(file.filename):    # 허용된 확장자인지
                filename = check_filename(file.filename)    # secure_filename
                file.save(os.path.join(app.config['BOARD_ATTACH_FILE_PATH'], filename))
        # 추가코드1 end 
        
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
        print(f'filename확인: {filename}')  # 연습.txt.txt
        # 추가코드2
        if filename is not None:
            post['attachfile'] = filename   # mongodb에 파일명을 저장하네 good
        # 추가코드2 end
        
        x = board.insert_one(post)

        # x.inserted_id >> ObjectId 자료형
        # return redirect(url_for("board_view", idx=x.inserted_id))
        return redirect(url_for("board.board_view", idx=x.inserted_id))
    else:
        return render_template("write.html", title="글작성")


@bp.route("/delete/<idx>")
def board_delete(idx):
    board = mongo.db.board
    data = board.find_one({"_id": ObjectId(idx)})
    if data is None:
        flash("해당 게시물이 존재 하지 않습니다")
    else:
        if session.get("id") == data.get("writer_id"):
            board.delete_one({"_id": ObjectId(idx)})
            flash("게시글이 삭제 되었습니다")
        else:
            flash("게시물 삭제 권한이 없습니다")
    return redirect(url_for("board.lists"))


@bp.route("/edit/<idx>", methods=("GET", "POST"))
def board_edit(idx):
    if request.method == "GET":
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if data is None:
            flash("해당 게시물이 존재 하지 않습니다")
            return redirect(url_for('board.lists'))
        else:
            if session.get('id') == data.get('writer_id'):
                # 이제 수정진행이지 : 로긴한사
                return render_template("edit.html", data=data, title='글수정')
            else:
                flash("글 수정 권한이 없습니다")
                return redirect(url_for('board.lists'))
    else:
        title = request.form.get('title', type=str)
        contents = request.form.get('contents', type=str)
        
        # 첨부파일 로직 
        deleteoldfile = request.form.get('deleteoldfile', '')   # 기본값이 '' 값인게 뭔가 포인트
        # 첨부파일 로직 end
        
        
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if data is None:
            flash('해당 게시물이 존재 하지 않습니다')
            return redirect(url_for('board.lists'))
        else:
            if session.get('id') == data.get('writer_id'):  # 수정 삭제 권한 확인
                # 첨부파일 로직 2 
                filename = None
                if 'attachfile' in request.files:   # 첨부파일이 있으면
                    file = request.files['attachfile']
                    if file and allowed_file(file.filename):
                        filename = check_filename(file.filename)
                        file.save(os.path.join(app.config['BOARD_ATTACH_FILE_PATH'], filename))

                        # 근데 db에 이미 저장된 파일이 있으면 삭제 해야지
                        if data.get("attachfile"):     # 파일이 있으면 == 예전파일
                            # mongodb를 지우는게 아니라, 서버에 저장된 파일을 지워야 하는구나
                            board_delete_attach_file(data.get("attachfile"))
                                # file삭제 함수
                else:   # 첨부파일 없을때
                    if deleteoldfile == "on":   #체크박스 체크한경우 == 파일삭제하라는경우
                        filename = None     # 파일삭제 관련 진행하니깐 로직들어가야함
                        if data.get('attachfile'):
                            board_delete_attach_file(data.get('attachfile'))
                    else:   # 삭제 하지말라고하면
                        filename = data.get("attachfile")                        
                # 첨부파일 로직 2 end
                    
                
                board.update_one({"_id": ObjectId(idx)}, {
                    "$set": {
                        "title": title,
                        "contents": contents,
                        # 첨부파일 로직 3 
                        'attachfile': filename                        
                        # 굳이 없데이트 해줘야 하나? >> 응 수정하니까 필요한거 다 수정해줘야해, 
                        # 첨부파일 로직 end 
                    }
                })
                flash('수정되었습니다.')
                return redirect(url_for("board.board_view", idx=idx))
            else:
                flash('수정권한이 없습니다')
                return redirect(url_for("board.lists"))


# 코멘트 작성
@bp.route("/comment_write", methods=["POST"])
@login_required
def comment_write():
    name = session.get('name')
    writer_id = session.get('id')
    comment = request.form.get('comment')
    root_idx = request.form.get("root_idx")     # root_idx : 글 id야
    current_utc_time = round(datetime.utcnow().timestamp() * 1000)
    
    c_comment = mongo.db.comment
    
    post = {
        "root_idx": str(root_idx),  # 글 id
        "writer_id" : writer_id,
        "name" : name,
        "comment": comment,
        "pubdate": current_utc_time
    }    
    
    c_comment.insert_one(post)
        
    return redirect(url_for('board.board_view', idx=root_idx))

# 코멘트리스트
@bp.route("/comment_list/<root_idx>", methods=["GET"])
def comment_list(root_idx):
    comment = mongo.db.comment
    comments = comment.find({"root_idx": root_idx}).sort("pubdate", -1)
    
    comment_list = []
    for c in comments:
        # 수정권한있는지
        owner = True if session.get('id') == c.get('writer_id') else False

        comment_list.append({
            'id': str(c.get('_id')),    # comment id
            'root_idx': c.get('root_idx'),  # 글id
            'name': c.get('name'),
            'writer_id': c.get('writer_id'),
            'comment': c.get('comment'),
            'pubdate': format_datetime(c.get('pubdate')),
            'owner' : owner
        })
        
    return jsonify(error='success', lists=comment_list)


# 코멘트삭제
@bp.route("/comment_delete", methods=['POST'])
@login_required
def comment_delete():
    if request.method == "POST":
        idx = request.form.get("id")
        
        comment = mongo.db.comment
        data = comment.find_one({"_id": ObjectId(idx)})
        # 권한 확인 다시해야된데
        if session.get('id') == data.get("writer_id"):
            comment.delete_one({"_id": ObjectId(idx)})
            return jsonify(error="success")
        else:
            return jsonify(error="error")
    else:
        abort(401)
            
            
