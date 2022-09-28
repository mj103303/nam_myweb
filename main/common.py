from functools import wraps
from main import session, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id') is None:
            return redirect(url_for('member.member_login', next_url=request.url))
        return f(*args, **kwargs)   #* 리턴으로 함수를 인자 넣어줘 줘야하는듯
    return decorated_function      