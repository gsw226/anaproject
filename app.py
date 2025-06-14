from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect
from flask_migrate import Migrate
from controller import hash_password
from controller import unhash_password
import re   
import click

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.String(500), nullable=False)

@app.cli.command()
def clear_data():
    """테이블 구조는 유지하고 데이터만 삭제"""
    if click.confirm('모든 데이터를 삭제하시겠습니까?'):
        # 외래키 제약조건을 고려한 순서로 삭제
        db.session.query(Post).delete()
        db.session.query(User).delete()
        db.session.commit()
        click.echo('🧹 데이터 삭제 완료!')

def get_user_info(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return user.id, user.password
    else:
        return None, None

@app.route("/",methods=['POST','GET'])
def index():
    uid = session.get('uid','')
    if uid == None or uid == "":
        return redirect('/sign')
    if request.method == 'POST':
        return render_template('index.html',uid=uid)
    return render_template('index.html', uid=uid)

@app.route('/board', methods=['GET'])
def board():
    uid = session.get('uid','')
    if uid == None or uid == "":
        return redirect('/sign')
    boards = Board.query.order_by(Board.id.desc()).all()
    return render_template('/board.html', boards=boards)

@app.route('/view', methods=['GET','POST'])
def view():
    uid = session.get('uid','')
    if uid == None or uid == "":
        return redirect('/sign')
    search_email = request.args.get('email')
    search_title = request.args.get('title')
    print(search_email, search_title)
    if (request.method == 'POST'):
        comment_content = request.form.get('comment')
        print(comment_content)
        if comment_content:
            new_comment = Comment(email=uid, title=search_title ,content=comment_content)
            db.session.add(new_comment)
            db.session.commit()
            return redirect('/view?email={}&title={}'.format(search_email, search_title))

    if search_email and search_title:
        boards = Board.query.filter_by(email=search_email, title=search_title).all()
        comments = Comment.query.filter_by(email=search_email, title=search_title).all()
    else:
        return redirect('/board')
    
    return render_template('view.html', boards=boards, comments=comments)

@app.route('/create', methods=['GET','POST'])
def create():
    uid = session.get('uid','')
    if uid == None or uid == "":
        return redirect('/sign')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if(content == None or title == None):
            return redirect('/board')
        new_create = Board(email=uid, title=title, content=content)
        db.session.add(new_create)
        db.session.commit()
        return redirect('/board')
    return render_template('create.html')

@app.route('/gsw',methods=['GET'])
def gsw():
    return render_template('gsw.html')

@app.route('/sign', methods=['POST', 'GET'])  # 이메일, 비밀번호 db로 전송
def sign():
    password_pattern = r'^(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).+$'
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        password_2 = request.form.get('password_2', '')
        
        # 필수 입력 항목 확인
        if email == '' or password == '' or password_2 == '':
            return render_template('sign.html', msg="이메일, 비밀번호, 비밀번호 확인을 모두 입력해주세요.")
        
        # 이메일 중복 확인
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('sign.html', msg="이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.")
        
        # 비밀번호 규칙 확인
        if not re.match(password_pattern, password):
            return render_template('sign.html', msg="비밀번호는 영문 대소문자, 숫자, 특수문자를 모두 포함해야 합니다.")
        
        # 비밀번호 일치 확인
        if password != password_2:
            return render_template('sign.html', msg="비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        
        # 회원가입 성공
        hashed_password = hash_password(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', msg="회원가입이 완료되었습니다. 로그인해주세요.")
    
    else:
        return render_template('sign.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_email = request.form['login_email']
        login_password = request.form['login_password']
        print(login_email)

        if not login_email or not login_password:
            return redirect('/login')

        user = User.query.filter_by(email=login_email).first()

        if user and unhash_password(login_password, user.password):
            session['uid'] = login_email
            return redirect('/')    
        else:
            return redirect('/login')
    else:
        return render_template('login.html')

@app.route('/mypage',methods=['POST','GET'])
def mypage():
    password_pattern = r'^(?=.[!@#$%^&(),.?":{}|<>])(?=.\d)(?=.[a-z])(?=.*[A-Z]).+$'

    uid = session.get('uid','')
    if uid == None or uid == "":
        return redirect('/sign')

    idx, hashed_password = get_user_info(uid)

    if request.method == 'POST':
        original_password = request.form['original_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not unhash_password(original_password, hashed_password):
            return render_template('mypage.html', msg="현재 비밀번호가 일치하지 않습니다.",uid=uid)

        if new_password != confirm_password or new_password=='' or confirm_password=='':
            return render_template('mypage.html',msg="비밀번호를 확인해주세요.",uid=uid)

        if re.match(password_pattern, new_password):
            user = User.query.filter_by(email=uid).first()
            user.password = hash_password(new_password)
            db.session.commit()
            return render_template('mypage.html', msg="비밀번호가 성공적으로 변경되었습니다.",uid=uid)
        else:
            return render_template('mypage.html', msg = "비밀번호 규칙을 확인하세요.",uid=uid) 
    return render_template('mypage.html',uid=uid)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)   