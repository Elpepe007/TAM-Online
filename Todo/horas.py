from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from Todo.auth import login_required, admin_login_required, profesor_login_required
from Todo.db import get_db
from flask import send_file
import pandas as pd
import os
from datetime import time

bp = Blueprint('horas', __name__)
#all_defs
def float_to_time(n):
    h, m = divmod(n * 60, 60)
    return time(int(h),int(m))

def get_alumno(nombre):
    db, c = get_db()
    c.execute('SELECT * FROM alumnos WHERE nombre = %s;', (nombre,))
    alumno = c.fetchone()
    if alumno is None:
        abort(404,"El alumno de nombre{0} no existe".format(id))
    return alumno

def time_to_string_float(time):
    if time == '00:00:00' or time == '0:00:00':
        return(float(0))
    h1, m1, s1= time.split(":")
    if h1 == 00:
        h2 = str(h1)
    else:
        h2 = str(h1).lstrip("0")    
    m2 = str(m1).lstrip("0")
    try:
        str(float(h2 + "." + m2))
        return str(float(h2 + "." + m2))
    except:
        return h2 + "." + m2

#all_defs_finish

@bp.route('/estudiantes_index')
@login_required
def estudiantes_index():
    db, c = get_db()
    c.execute('SELECT * FROM alumnos ORDER BY nombre ASC;') 
    alumnos = c.fetchall()  
    for i in alumnos:
        i['horas'] = time_to_string_float(str(i['horas']))
    return render_template('user_estudiante/index.html', alumnos=alumnos)


@bp.route('/profesor_register_index',methods=['GET','POST'])
@admin_login_required
def profesor_register_index():
    db, c = get_db()
    c.execute("SELECT id, username FROM user WHERE NOT EXISTS (SELECT 1 FROM profesores WHERE profesores.user_id = user.id ) AND user.user_type = 'profesor' ") 
    users = c.fetchall()
    return render_template('auth/user_admin/user_index.html', users=users)


@bp.route('/<ID_DEL_USER>/<NOMBRE_DEL_USER>/profesor_register',methods=['GET','POST'])
@admin_login_required
def profesor_register(ID_DEL_USER,NOMBRE_DEL_USER):
    db, c = get_db()    
    c.execute('SELECT id, nombre FROM talleres;')
    talleres = c.fetchall()    
    if request.method == 'POST':
        db, c = get_db()
        taller = int(request.form['taller']) 
        c.execute("INSERT INTO profesores (user_id, taller_id) VALUES (%s, %s);",(ID_DEL_USER, taller))
        db.commit()
        return redirect(url_for('horas.profesor_register_index'))
    return render_template('auth/user_admin/user_register.html', talleres=talleres, ID_DEL_USER=ID_DEL_USER, NOMBRE_DEL_USER=NOMBRE_DEL_USER)

@bp.route('/<int:ID_DEL_USER>/profesor_delete',methods=['GET','POST'])
@admin_login_required
def profesor_delete(ID_DEL_USER):
    db, c = get_db()
    c.execute('delete from user where id = %s',(ID_DEL_USER,))
    db.commit()
    return redirect(url_for('horas.profesor_register_index'))

@bp.route('/')
@profesor_login_required
def index():
    db, c = get_db()
    c.execute('SELECT * FROM alumnos WHERE taller_id = %s ORDER BY nombre ASC;',(g.user_taller_id,)) 
    alumnos = c.fetchall()
    for i in alumnos:
        i['horas'] = time_to_string_float(str(i['horas']))
    c.execute('SELECT nombre FROM talleres WHERE id = %s;',(g.user_taller_id,))
     
    return render_template('horas/index.html', alumnos=alumnos)

@bp.route('/create', methods=['GET','POST'])
@profesor_login_required
def create():
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        horas = float_to_time(float(0))
        error = None        
        if not nombre:
            error = 'El nombre es requerido'
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('INSERT INTO alumnos (nombre, taller_id, horas) VALUES (%s, %s, %s)',(nombre, g.user_taller_id, horas))
            db.commit()
            return redirect(url_for('horas.index'))

    return render_template('horas/create.html', error=error)

@bp.route('/<nombre>/update', methods=['GET','POST'])
@profesor_login_required
def update(nombre):
    alumno = get_alumno(nombre)
    error = None
    if request.method == 'POST':
        horas = int(request.form['horas'])
        minutos = int(request.form['minutos'])
        error = None
        if not minutos and not horas:
            error = 'horas requeridas para actualizar'         
        if minutos < 0 and horas > 0 or minutos > 0 and horas < 0:
               error = 'no podes tener una opccion en negativo y otra en positivo'
        if minutos < 0 or horas < 0 :
            minutos1 = abs(minutos)
            horas1 = abs(horas)
            numero_de_horas = "{:02d}:{:02d}:00".format(horas1, minutos1)        
            if (float(time_to_string_float(str(alumno['horas']))) - float(time_to_string_float(numero_de_horas))) < 0:
                error = 'no podes tener a un alumno en negativo' 
        if error is not None:
            flash(error)
        else:
            if minutos < 0 or horas < 0 :
                minutos = abs(minutos)
                horas = abs(horas)
                numero_de_horas = "{:02d}:{:02d}:00".format(horas, minutos)
                db, c = get_db()
                c.execute('UPDATE alumnos SET horas = SUBTIME(horas, %s) WHERE nombre = %s AND taller_id = %s',(numero_de_horas,nombre,g.user_taller_id))
                db.commit()
            else:
                numero_de_horas = "{:02d}:{:02d}:00".format(horas, minutos)
                db, c = get_db()
                c.execute('UPDATE alumnos SET horas = ADDTIME(horas, %s) WHERE nombre = %s AND taller_id = %s',(numero_de_horas,nombre,g.user_taller_id))
                db.commit()    

            return redirect(url_for('horas.index'))
    return render_template('horas/update.html', alumno=alumno, error=error)

@bp.route('/<nombre>,<int:number>/update_by_button', methods=['GET','POST'])
@profesor_login_required
def update_by_button(nombre,number):    
    error = None
    try:
        float(number)
    except:
        error = 'Pone solo un numero y en vez de una coma utiliza un punto'    
    if error is not None:
        flash(error)
    else:
        horas_request = float_to_time(float(number))
        db, c = get_db()
        c.execute('UPDATE alumnos SET horas = ADDTIME(horas, %s) WHERE nombre = %s AND taller_id = %s',(horas_request,nombre,g.user_taller_id))
        db.commit()
        return redirect(url_for('horas.index'))

@bp.route('/<string:nombre>/delete', methods=['POST'])
@profesor_login_required
def delete(nombre):
    db, c = get_db()
    c.execute('delete from alumnos where nombre = %s and taller_id = %s',(nombre, g.user_taller_id))
    db.commit()
    return redirect(url_for('horas.index'))

def database_to_csv():
    db, c = get_db()
    c.execute('SELECT nombre, horas FROM alumnos WHERE taller_id = %s;',(g.user_taller_id,))
    database_table = c.fetchall()
    for i in database_table:
        i['horas'] = float(time_to_string_float(str(i['horas'])))
    df = pd.DataFrame(database_table)
    df.to_excel(r'./Todo/csv_outputs/exported_data.xlsx', index = False)

@bp.route('/csv_export', methods=['GET','POST'])
@profesor_login_required
def csv_export():
    try:
        os.remove(r'./Todo/csv_outputs/exported_data.xlsx')
    except:
        pass

    database_to_csv()

    return send_file(r'csv_outputs/exported_data.xlsx', as_attachment=True, download_name='data.xlsx')

@bp.route('/reiniciar_semana', methods=['GET','POST'])
@profesor_login_required
def reiniciar_semana():
    db, c = get_db()
    c.execute('SELECT nombre FROM alumnos WHERE taller_id = %s;',(g.user_taller_id,))
    alumnos = c.fetchall()
    for i in alumnos:
        nombre = i['nombre']
        c.execute('UPDATE alumnos SET horas = "00:00:00" WHERE nombre = %s AND taller_id = %s',(nombre,g.user_taller_id))
    db.commit()
    return redirect(url_for('horas.index'))
