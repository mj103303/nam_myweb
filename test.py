from flask import request
import re, os

def check_filename(filename):
    reg = re.compile("[^a-zA-Z_.가-힝-]")   # 문자가 아닌걸 담음
    for s in os.path.sep, os.path.altsep:
        if s:   # 무조건 하는데, 두번하네
            filename = filename.replace(s, ' ')
            print("replace:",filename)
            filename = filename.split() # 리스트 만듬
            print("split:",filename)            
            filename = '_'.join(filename)   # _ 조인 : ex) a_b_c
            print("join:",filename)            
            filename = reg.sub('', filename)   
            print("정규식적용:",filename)            
                # filename 에 이상한 문자가 있으면 -> '' 교체
                # sub이 교체하는거였어 (교체할 문자 , 매칭되는 대상)
            filename = str(filename).strip('._')    # ._ 이런문자가 생긴데 그래서 strip
    return filename