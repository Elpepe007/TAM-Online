import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=  'session_name',
        DATABASE_HOST= os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD= os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER= os.environ.get('FLASK_DATABASE_USER'),
        DATABASE= os.environ.get('FLASK_DATABASE'),
        DATABASE_PORT=os.environ.get('FLASK_DATABASE_PORT')
        )
    from . import db
    db.init_app(app)

    from . import auth
    from . import horas

    app.register_blueprint(auth.bp)
    app.register_blueprint(horas.bp)

    @app.route('/hola')
    def hola():
        return 'encontraste el easter egg de tatu'


    return app
'''
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

'''