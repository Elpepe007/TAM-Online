import functools
from flask import Blueprint, flash, g, render_template, request, url_for, session, redirect, abort, Response
from werkzeug.security import  check_password_hash, generate_password_hash
from Todo.db import get_db

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register',methods=['GET','POST'])
def register():
    db, c = get_db()    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        Type = int(request.form['user_type'])
        db, c = get_db()
        error = None
        c.execute("SELECT id FROM user WHERE username = %s", (username,))
        if not username:
            error = 'Username es requerido'
        if not password:
            error = 'Password es requerido'
        if Type == 0 or Type > 2:
            error = 'El tipo de usuario es requerido'        
        elif c.fetchone() is not None:
            print(c.fetchone())
            error = 'Usuario {} ya se registro antes'.format(username)
        if error is None:
            user_type = None
            if Type == 1:
                user_type = 'profesor'
            if Type == 2:
                user_type = 'estudiante'
            c.execute("INSERT INTO user (username, password, user_type) VALUES (%s, %s, %s)",(username, generate_password_hash(password), user_type))
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)

    return render_template('auth/Register_v2/index.html')

    
@bp.route('/login',methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db,c = get_db()
        error = None
        c.execute('select * from user where username = %s', (username,))
        user = c.fetchone()
        c.execute('SELECT taller_id FROM profesores WHERE user_id = (SELECT id FROM user WHERE username = %s)',(username,))
        user_taller_id = c.fetchone()
        if user is None:
            error = 'Username or Password incorrect'
        elif not check_password_hash(user['password'], password):
            error = 'Username or Password incorrect'
        if error is None:
            try:
                if user['user_type'] == 'profesor': 
                    session['user_taller_id'] = user_taller_id['taller_id']        
            except:
                abort(Response('El Profesor todavia no tiene asignado el taller'))
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            if user['user_type'] == 'profesor': 
                session['user_taller_id'] = user_taller_id['taller_id']
            if user['username'] == 'admin':
                return redirect(url_for('horas.profesor_register_index'))
            if user['user_type'] == 'estudiante':
                return redirect(url_for('horas.estudiantes_index'))
            else:            
                return redirect(url_for('horas.index'))
        flash(error)
    return render_template('auth/Login_v2/index.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    user_taller_id = session.get('user_taller_id')
    user_type = session.get('user_type')
    if user_id is None:
        g.user = None
        g.user_taller_id = None
        g.nombre_taller = None
        g.user_type = None
    else:
        db, c = get_db()
        c.execute('select * from user where id = %s', (user_id,))
        g.user = c.fetchone()
        g.user_taller_id = user_taller_id
        c.execute('SELECT nombre FROM talleres WHERE id = %s',(g.user_taller_id,))
        g.nombre_taller = c.fetchone()
        g.user_type = user_type
        
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view 

def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user_type != 'admin':
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view 

def profesor_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user_type != 'profesor':
            session.clear()
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))