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
        ' WHERE t.status = "ACTIVE"'
        ' ORDER BY created DESC'
    ).fetchall()

    todo_items = []
    for todo in todos:
        per = get_percentage_complete(int(todo['id']))
        todo = dict(todo)
        todo.update({'complete': per})
        todo_items.append(todo)

    return render_template('todo/index.html', todos=todo_items)


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
    # Get todo list
    todo = get_db().execute(
        'SELECT t.id, t.user_id, t.name, t.description, t.created, t.status'
        ' FROM todo t JOIN user u ON t.user_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    # Check if List Exist and belongs to request Owner
    if todo is None:
        abort(404, f"Post id {id} doesn't exist.")
    elif check_user and todo['user_id'] != g.user['id']:
        abort(403)

    # Get todo List Items
    lists = None
    lists = get_db().execute(
        'SELECT l.id, l.name, l.created, l.status'
        ' FROM list l JOIN todo t ON l.todo_id = t.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchall()

    # Check if list is completed
    count = 0
    for item in lists:
        if item["status"] == "NOT_DONE":
            count += 1
            break
            
    if todo['status'] != "ACTIVE" and count > 0:
        # Set List Active 
        change_todo_status(id, 'ACTIVE')
        todo = dict(todo)
        todo.update({'status': 'ACTIVE'}) # todo['status'] = "ACTIVE"
    elif todo['status'] not in ["COMPLETE", "ARCHIVE"] and count == 0:
        # Set List Complete
        change_todo_status(id, 'COMPLETE')
        todo = dict(todo)
        todo.update({'status': 'COMPLETE'}) # ['status'] = "COMPLETE"



    return {'todo': todo, 'lists': lists}


@bp.route('/<int:id>/list', methods=('GET', 'POST'))
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


@bp.route('/<int:id>/list/<int:list_id>/delete')
@login_required
def delete_list(id, list_id):
    todo = get_todo(id)['todo']
    db = get_db()
    db.execute('DELETE FROM list WHERE id = ?', (list_id,))
    db.commit()
    flash('List Item Deleted.')
    return redirect(url_for('todo.detail', id=id))


@bp.route('/<int:id>/list/<int:list_id>/check')
@login_required
def check_list(id, list_id):
    get_todo(id)
    db = get_db()
    db.execute('UPDATE list SET status = ? WHERE id = ?', ('COMPLETE', list_id))
    db.commit()
    flash('List Item Checked.')
    return redirect(url_for('todo.detail', id=id))


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    todo = get_todo(id)['todo']

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required.'

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
            flash("{} List updated".formart(name))
            return redirect(url_for('todo.detail', id=id))

    return render_template('todo/update.html', todo=todo)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_todo(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('todo.index'))


@bp.route('/<int:id>/archive')
@login_required
def archive(id):
    # get todo data
    todo = get_todo(id)["todo"]
    # check if list is completed
    if todo["status"] == 'COMPLETE':
        db = get_db()
        db.execute('UPDATE todo SET status = ? WHERE id = ?', ('ARCHIVE', id))
        db.commit()
        flash('List Archived.')
    else:
        flash('Error: Some Items in the list are unchecked')
    return redirect(url_for('todo.detail', id=id))


@bp.route('/archives')
@login_required
def archives():
    db = get_db()
    todos = db.execute(
        'SELECT t.id, name, description, created, status'
        ' FROM todo t JOIN user u ON t.user_id = u.id'
        ' WHERE t.status = "ARCHIVE"'
        ' ORDER BY created DESC'
    ).fetchall()

    todo_items = []
    for todo in todos:
        per = get_percentage_complete(int(todo['id']))
        todo = dict(todo)
        todo.update({'complete': per})
        todo_items.append(todo)

    return render_template('todo/index.html', todos=todo_items, status="ARCHIVE")


def change_todo_status(id, status):
    db = get_db()
    db.execute('UPDATE todo SET status = ? WHERE id = ?', (status, id))
    db.commit()


def get_percentage_complete(id):
    lists = get_todo(id)['lists']
    count = 0
    for item in lists:
        if item['status'] == 'COMPLETE':
            count += 1

    # calcuate percentage complete
    if count > 0:
        complete = (count/len(lists)) * 100 
        return int(complete)
    return count