from functools import wraps
from main import ALLOWED_EXTENSIONS, session, redirect, url_for, request
from string import digits, ascii_uppercase, ascii_lowercase
import random
import re, os
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)

# os.path.sep : \
# os.path.altsep : /
def check_filename(filename):
    reg = re.compile("[^a-zA-Z_.가-힝-]")   # 문자가 아닌걸 담음
    for s in os.path.sep, os.path.altsep:
        if s:   # 무조건 하는데, 두번하네
            filename = filename.replace(s, ' ')
            filename = filename.split() # 리스트 만듬
            filename = '_'.join(filename)   # _ 조인 : ex) a_b_c
            filename = reg.sub('', filename)   
                # filename 에 이상한 문자가 있으면 -> '' 교체
                # sub이 교체하는거였어 (교체할 문자 , 매칭되는 대상)
            filename = str(filename).strip('._')    # ._ 이런문자가 생긴데 그래서 strip
    return filename

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id') is None:
            return redirect(url_for('member.member_login', next_url=request.url))
        return f(*args, **kwargs)   #* 리턴으로 함수를 인자 넣어줘 줘야하는듯
    return decorated_function      


def allowed_file(filename):
    '''허용된 파일 확장자인지확인'''
    return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS

def rand_generate(length=8):
    char = digits + ascii_uppercase + ascii_lowercase
    return ''.join(random.sample(char, length)) 



