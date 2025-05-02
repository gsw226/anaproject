from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect
from flask_migrate import Migrate
from controller import hash_password
from controller import unhash_password
import re

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

@app.route("/",methods=['POST','GET'])
def index():
    uid = session.get('uid','')
    if uid == None or uid == "":
        return redirect('/sign')
    if request.method == 'POST':
        return render_template('index.html',uid=uid)
    return render_template('index.html', uid=uid)


@app.route('/sign', methods=['POST', 'GET'])  # 이메일, 비밀번호 db로 전송
def sign():
    password_pattern = r'^(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).+$'
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        password_2 = request.form.get('password_2', '')
        
        if email == '' or password == '':
            return render_template('/sign.html' , msg = "아이디 또는 비밀번호를 입력하세요.")
        
        if re.match(password_pattern, password):
            if password == password_2:
                hashed_password = hash_password(password)
                user = User.query.filter_by(email=email).first()
                if user != email:
                    new_user = User(email=email, password=hashed_password)
                    db.session.add(new_user)
                    db.session.commit()
                    return render_template('login.html', msg = "성공적으로 회원가입 완료")
                else:
                    return render_template('sign.html', msg = "이메일이 중복 됩니다.")
            else: 
                return render_template('sign.html', msg = "비밀번호가 일치하지 않습니다.")
        else:
            return render_template('sign.html', msg = "비밀번호 규칙을 확인하세요.")
    else:
        return render_template('sign.html')


@app.route('/login', methods=['POST','GET']) # 이메일, 비밀번호
def login():
    if request.method == 'POST':
        login_email = request.form['login_email']
        login_password = request.form['login_password']
        print(login_email)
        user = User.query.filter_by(email=login_email).first()
        if user.email == login_email:
            if unhash_password(login_password,user.password):
                session['uid'] = login_email
                return redirect('/') 
            else:
                return render_template('login.html')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)