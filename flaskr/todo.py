from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('todo', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    todos = db.execute(
        'SELECT t.id, name, description, created, status'
        ' FROM todo t JOIN user u ON t.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('todo/index.html', todos=todos)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO todo (name, description, user_id)'
                ' VALUES (?, ?, ?)',
                (name, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')


def get_todo(id, check_user=True):
    todo = get_db().execute(
        'SELECT t.id, t.name, t.description, t.created, t.status'
        ' FROM todo t JOIN user u ON t.user_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    lists = None
    if todo is None:
        abort(404, f"Post id {id} doesn't exist.")
    else:
        lists = get_db().execute(
            'SELECT l.id, l.name, l.created, l.status'
            ' FROM list l JOIN todo t ON l.todo_id = t.id'
            ' WHERE t.id = ?',
            (id,)
        ).fetchall()

    if check_user and id != g.user['id']:
        abort(403)

    return {'todo': todo, 'lists': lists}


@bp.route('/<int:id>/detail', methods=('GET', 'POST'))
@login_required
def detail(id):
    if request.method == 'POST':
        get_todo(id)
        new_list = dict(request.form)
        list_num = new_list.pop('list_num')
        for name in new_list.values():
            db = get_db()
            db.execute(
                'INSERT INTO list (name, todo_id)'
                ' VALUES (?, ?)',
                (name, id)
            )
            db.commit()

    todo = get_todo(id)
    return render_template('todo/detail.html', todo=todo['todo'], lists=todo['lists'])



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    todo = get_todo(id)['todo']

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE todo SET name = ?, description = ?'
                ' WHERE id = ?',
                (name, description, id)
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_todo(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('todo.index'))
