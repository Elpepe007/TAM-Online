from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from Todo.auth import login_required, admin_login_required
from Todo.db import get_db
from flask import send_file
import pandas as pd
import os

bp = Blueprint('horas', __name__)

@admin_login_required
@bp.route('/profesor_register_index',methods=['GET','POST'])
def profesor_register_index():
    db, c = get_db()
    c.execute('SELECT id, username FROM user WHERE NOT EXISTS (SELECT 1 FROM profesores WHERE profesores.user_id = user.id )') 
    users = c.fetchall()
    return render_template('auth/user_admin/user_index.html', users=users)

@admin_login_required
@bp.route('/<ID_DEL_USER>/<NOMBRE_DEL_USER>/profesor_register',methods=['GET','POST'])
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

@admin_login_required
@bp.route('/<int:ID_DEL_USER>/profesor_delete',methods=['GET','POST'])
def profesor_delete(ID_DEL_USER):
    db, c = get_db()
    c.execute('delete from user where id = %s',(ID_DEL_USER,))
    db.commit()
    return redirect(url_for('horas.profesor_register_index'))

@bp.route('/')
@login_required
def index():
    db, c = get_db()
    c.execute('SELECT * FROM alumnos WHERE taller_id = %s ORDER BY nombre ASC;',(g.user_taller_id,)) 
    alumnos = c.fetchall()
    c.execute('SELECT nombre FROM talleres WHERE id = %s;',(g.user_taller_id,))
    taller = c.fetchone()
     
    return render_template('horas/index.html', alumnos=alumnos, taller=taller)

@bp.route('/create', methods=['GET','POST'])
@login_required
def create():
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        horas = None
        error = None        

        try:
            horas = int(request.form['horas'])
        except:
            error = 'Solo se aceptan numeros'

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


def get_alumno(nombre):
    db, c = get_db()
    c.execute('SELECT * FROM alumnos WHERE nombre = %s;', (nombre,))
    alumno = c.fetchone()
    if alumno is None:
        abort(404,"El alumno de nombre{0} no existe".format(id))
    return alumno

@bp.route('/<nombre>/update', methods=['GET','POST'])
@login_required
def update(nombre):
    alumno = get_alumno(nombre)
    error = None
    if request.method == 'POST':
#        alumno = get_alumno(nombre)
        numero_de_horas = request.form['horas']
        error = None
        if not numero_de_horas:
            error = 'horas requeridas para actualizar'
        try:
            float(numero_de_horas)
        except:
            error = 'Pone solo un numero y en vez de una coma utiliza un punto'    
        if error is not None:
            flash(error)
        else:
            horas_finales = float(alumno['horas']) + float(numero_de_horas)
            db, c = get_db()
            c.execute('UPDATE alumnos SET horas = %s WHERE nombre = %s AND taller_id = %s',(horas_finales,nombre,g.user_taller_id))
            db.commit()
            return redirect(url_for('horas.index'))
    return render_template('horas/update.html', alumno=alumno, error=error)


@bp.route('/<nombre>,<int:number>/update_by_button', methods=['GET','POST'])
@login_required
def update_by_button(nombre,number):
    alumno = get_alumno(nombre)
    error = None
    try:
        float(number)
    except:
        error = 'Pone solo un numero y en vez de una coma utiliza un punto'    
    if error is not None:
        flash(error)
    else:
        horas_finales = float(alumno['horas']) + float(number)
        db, c = get_db()
        c.execute('UPDATE alumnos SET horas = %s WHERE nombre = %s AND taller_id = %s',(horas_finales,nombre,g.user_taller_id))
        db.commit()
        return redirect(url_for('horas.index'))



@bp.route('/<string:nombre>/delete', methods=['POST'])
@login_required
def delete(nombre):
    db, c = get_db()
    c.execute('delete from alumnos where nombre = %s and taller_id = %s',(nombre, g.user_taller_id))
    db.commit()
    return redirect(url_for('horas.index'))

def database_to_csv():
    db, c = get_db()
    c.execute('SELECT nombre, horas FROM alumnos WHERE taller_id = %s;',(g.user_taller_id,))
    database_table = c.fetchall()
    df = pd.DataFrame(database_table)
    df.to_excel(r'.\Todo\csv_outputs\exported_data.xlsx', index = False)


@bp.route('/csv_export', methods=['GET','POST'])
@login_required
def csv_export():
    try:
        os.remove(r'.\Todo\csv_outputs\exported_data.xlsx')
    except:
        pass

    database_to_csv()

    return send_file(r'csv_outputs\exported_data.xlsx', index = False, as_attachment=True, download_name='data.xlsx')

@bp.route('/reiniciar_semana', methods=['GET','POST'])
@login_required
def reiniciar_semana():
    db, c = get_db()
    c.execute('SELECT nombre FROM alumnos WHERE taller_id = %s;',(g.user_taller_id,))
    alumnos = c.fetchall()
    for i in alumnos:
        nombre = i['nombre']
        c.execute('UPDATE alumnos SET horas = %s WHERE nombre = %s AND taller_id = %s',(0,nombre,g.user_taller_id))
    db.commit()
    return redirect(url_for('horas.index'))
