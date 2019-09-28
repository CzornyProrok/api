from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, render_template_string
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from requestium import Session, Keys
from bs4 import BeautifulSoup
import requests
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'torrent'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Init MySQL
mysql = MySQL(app)


@app.route('/test')
def index():
    mycursor = mysql.connection.cursor()
    myresult=mycursor.execute("SELECT * FROM search")
    if myresult > 0:
        myresultfin = mycursor.fetchall()
        print(myresultfin)
        return render_template('test.html', myresultfin=myresultfin)







@app.route('/about')
def about():
    return render_template('about.html')


class RegisterForm(Form):
    login = StringField('Login', [
        validators.DataRequired(),
        validators.Length(min=5, max=25)])
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=75)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


class HistoryForm(Form):
    historyname = StringField('torname', [
        validators.DataRequired(),
        validators.Length(min=1, max=500)
    ])
    historyurl = StringField('url', [
        validators.DataRequired(),
        validators.Length(min=1, max=500)
    ])
    historymagnet = StringField('magnet', [
        validators.DataRequired(),
        validators.Length(min=1, max=500)
    ])
    historyseeds = StringField('seeds', [
        validators.DataRequired(),
        validators.Length(min=1, max=500)
    ])
    searchcount = StringField('searchcount', [
        validators.DataRequired(),
        validators.Length(min=1, max=500)
    ])
# Register form class


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        login = form.login.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        active = 1

        # Create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(login, email, password, active) VALUES(%s, %s, %s, %s)", (login, email, password, active))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        redirect(url_for('index'))
    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get form fields
        login = request.form['login']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM user WHERE login = %s", [login])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['login'] = login
                return redirect(url_for('dashboard'))
            else:
                error = 'Username or password did not match'
                cur.close()
                return render_template('login.html', error=error)
        else:
            error = 'Username or password did not match'
            return render_template('login.html', error=error)
    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unathorized access denied', 'danger')
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.route('/torrent_result', methods=["GET", "POST"])
@app.route('/torrent_form', methods=["GET", "POST"])
def torrent_form():
    try:
        if request.method == 'POST':
            name = request.form['name']
            s = Session(webdriver_path=r"C:/Users/kubak/Downloads/chromedriver.exe",
                        browser='chrome',
                        webdriver_options={
                            'arguments': [
                                'disable-dev-shm-usage',
                                'headless',
                                'no-sandbox'
                            ]
                        })
            url = 'https://torlock.com'
            s.driver.get(url)
            s.driver.ensure_element_by_name('q').send_keys([name, Keys.ENTER])
            r = requests.get(s.driver.current_url)
            soup = BeautifulSoup(r.text, 'lxml')
            torlocksearch = soup.find(class_='panel panel-default')
            torlock = torlocksearch.b.getText()
            torlockseeds = torlocksearch.find(class_='tul').getText()
            torlocktemp = torlocksearch.td
            torlockhref = torlocktemp.a.get('href')
            torlockdownload = url + torlockhref
            s.driver.get(torlockdownload)
            torlocksite = requests.get(s.driver.current_url)
            torlocksoup = BeautifulSoup(torlocksite.text, 'lxml')
            torlockdownloadsearch = torlocksoup.find(class_='table table-condensed')
            torlockmagnet = torlockdownloadsearch.a.get('href')

            url2 = 'https://thepiratebay.org'
            s.driver.get(url2)
            s.driver.ensure_element_by_tag_name('input').send_keys([name, Keys.ENTER])
            x = requests.get(s.driver.current_url)
            soup2 = BeautifulSoup(x.text, 'lxml')
            piratesearch = soup2.find(class_='detLink').getText()
            piratesearch2 = soup2.find(class_='detLink')
            temp3 = piratesearch2.get('href')
            baylink = url2 + temp3
            seeds2 = soup2.find('td', {'align': 'right'}).getText()
            s.driver.get(baylink)
            w = requests.get(baylink)
            soup3 = BeautifulSoup(w.text, 'lxml')
            download = soup3.find(class_='download')
            link3 = download.find('a')
            magnet2 = link3.get('href')
            # print(torlockseeds)
            # print(seeds2)
            if int(torlockseeds) > int(seeds2):
                url = torlockdownload
                stats = torlockseeds
                torname = torlock
                magnet = torlockmagnet
            else:
                url = baylink
                stats = seeds2
                torname = piratesearch
                magnet = magnet2
            s.close()
            return render_template('torrent_form.html', url=url, stats=stats, torname=torname, magnet=magnet)
        return render_template('torrent_form.html')
    except (Exception, ValueError):
        message = "Torrent not found"

        return render_template('torrent_form.html', message=message)


if __name__ == '__main__':
    app.secret_key = "secret123"
    app.run(debug=True)
