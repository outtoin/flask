# -*- coding: utf-8 -*-
# all the imports
from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash
from contextlib import closing
import os
import urllib2
import HTMLParser
from bs4 import BeautifulSoup
import re

# configuration
DATABASE = "C:\Users\outtoin\Desktop\\flaskr\\flaskr.db"
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'outtoin'
PASSWORD = 'dlqmsdl1017'

# API configuration
client_id = "H33urDm7HsBZnMNYAJQp"
client_secret = "0yyGwBVNLK"
url = "https://openapi.naver.com/v1/search/book.xml?query=" + '%EC%86%8C%EC%84%A4'
display = 30


url = url + "&display=" + str(display)
nrequest = urllib2.Request(url)

# API Authentication
nrequest.add_header("X-Naver-Client-Id", client_id)
nrequest.add_header("X-Naver-Client-Secret", client_secret)


# html stripper
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


# create application
app = Flask(__name__)
app.config.from_object(__name__)

# other configuration
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    init_db()
    g.db = connect_db()

    # API data -> database
    response = urllib2.urlopen(nrequest)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        body = response_body.decode('utf-8')
        soup = BeautifulSoup(body, 'html.parser')
        for i in soup.find_all('item'):
            isbn = i.find('isbn')
            title = i.find('title')
            author = i.find('author')
            description = i.find('description')

            jisbn = ''.join(isbn)
            jtitle = ''.join(title)
            jauthor = ''.join(author)
            jdescription = ''.join(description)

            jisbn = remove_html_tags(jisbn)
            jisbns = jisbn.split(" ")
            jtitle = remove_html_tags(jtitle)
            jauthor = remove_html_tags(jauthor)
            jdescription = remove_html_tags(jdescription)

            g.db.execute('insert into entries (isbn, title, author, description) '
                         'values (?, ?, ?, ?)',
                         [jisbns[1], jtitle, jauthor, jdescription])

    else:
        print("Error Code:" + rescode)

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select isbn, title, author, description from entries')
    entries = [dict(isbn=row[0], title=row[1], author=row[2], description=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

'''
@app.route('/add', methods = ['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
'''

@app.route('/book', methods=['GET'])
def book():
    cur = g.db.execute('select title, author, description from entries where isbn=' + format(request.args.get('isbn')))
    entries = [dict(title=row[0], author=row[1], description=row[2]) for row in cur.fetchall()]
    cur2 = g.db.execute('select title, author from entries limit 5')
    r_entries = [dict(title=row[0], author=row[1]) for row in cur2.fetchall()]
    return render_template('book.html', entries=entries, r_entries=r_entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()