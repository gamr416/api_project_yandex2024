from flask import Flask
from flask import render_template, redirect, request, abort, flash, url_for
from data import db_session
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import sqlite3
from sqlalchemy import desc

import os
from data.users import User
from data.news import News
#from data.answers import Answers


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = '/uploaded_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/add_comment', methods=['GET', 'POST'])
def add_comment():
    '''answer = request.form['answer']
    new_data = Answers(content=answer)
    db_sess = db_session.create_session()
    db_sess.add(new_data)
    db_sess.commit()'''

    return render_template('comment.html')


@app.route('/show_questions', methods=['GET', 'POST'])
def show():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    db_sess2 = db_session.create_session()

    news = db_sess2.query(News).order_by(News.created_date.desc()).all()
    """user_id = request.form['user_id']
    print(2)
    news_id = request.form['news_id']
    print(user_id)
    print(news_id)"""
    return render_template('all_questions.html', news=news, users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/question/<int:id>', methods=['GET', 'POST'])
def open_question(id):
    form = NewsForm()
    if request.method == 'POST':
        # check if the post request has the file part
        answer = request.files['answer']
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            form.news_id = news.id
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            news.id = form.news_id
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('question.html', title=f'Мыло: {form.title.data}', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user')
@login_required
def open_user():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('user_info.html', title=f'Мыло: {current_user.name}')


@app.route("/user/<int:id>")
def open_another_user(id):
    print(id)
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id
                                          ).first()
        if user:
            nickname = user.name
            avatar = user.avatar
            about = user.about
        else:
            abort(404)
    return render_template('another_user_info.html', title=f'{nickname}',
                           avatar=avatar, nickname=nickname, about=about)



@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        file = request.files['file']
        file.filename = f"avatar_{current_user.id}.png"
        avatar = f'static/img/uploaded_files/{file.filename}'
        file.save(avatar)
        con = sqlite3.connect('db/blogs.db')
        cur = con.cursor()
        cur.execute(f'''UPDATE users SET avatar = "{avatar}" WHERE id = "{current_user.id}"''')
        con.commit()
        cur.close()
        return redirect('/user')


@app.route('/success_answer/<int:id>', methods=['POST'])
def success_answer(id):
    if request.method == 'POST':
        answer = request.form
        con = sqlite3.connect('db/blogs.db')
        cur = con.cursor()
        answer_id = id
        cur.execute(
            f'''INSERT INTO answers (user_id, question_id, text) VALUES ({current_user.id}, {answer_id}, "{str(answer)[32:-4]}")''')
        cur.execute('''INSERT INTO news(answer_id) VALUES(?)''', (2, ))
        con.commit()
        cur.close()
    return redirect(f'/question/{id}')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        avatar = "static/img/no_image.png"
        con = sqlite3.connect('db/blogs.db')
        cur = con.cursor()
        cur.execute(f'''UPDATE users SET avatar = "{avatar}" WHERE id = "{user.id}"''')
        con.commit()
        cur.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/ask',  methods=['GET', 'POST'])
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Ваш вопрос',
                           form=form)


@app.route('/ask/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Изменение вопроса',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user != current_user) & (News.is_private != True)).order_by(desc(News.created_date))
    else:
        news = db_sess.query(News).filter(News.is_private != True).order_by(desc(News.created_date))
    return render_template("index.html", news=news, title=f'Мыло')


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()


