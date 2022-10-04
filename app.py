# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# global variable
post_input = []


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, title, text, category from entries order by id desc')
    entries = cur.fetchall()
    db_categories = db.execute('select distinct category from entries')
    categories = db_categories.fetchall()
    if len(post_input) != 0:
        if post_input[-1] != 'All':
            db_filter = db.execute("select id, title, text, category from entries where category = (?) ",
                                   (post_input[-1],))
            entries = db_filter.fetchall()

    return render_template('show_entries.html', entries=entries, categories=categories)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    category_input = request.form['category']
    if category_input == '':
        category_input = 'Not Specified'
    db.execute('insert into entries (title, text, category) values (?, ?, ?)',
               (request.form['title'], request.form['text'], category_input))
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/get', methods=['GET'])
def category():
    values = request.args.get('Select_category')
    post_input.append(values)
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete():
    db = get_db()
    deleted_value = request.get_json()['answer']
    db.execute('DELETE FROM entries WHERE entries.id = (?)', (deleted_value,))
    db.commit()
    return redirect(url_for('show_entries'))
