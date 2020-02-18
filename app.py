import json, re, csv
from flask import Flask, render_template, request, redirect, url_for, flash, stream_with_context, g, session
from flask_restful import Resource, Api
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jsonpify import jsonify
from json import dumps
from datetime import datetime
from io import StringIO
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
from ldap3 import *
from ldap3.core.exceptions import LDAPCursorError
#from flask_celery import make_celery
from celery import Celery


app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = "flash message"


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app.config['MYSQL_HOST'] = 'mysqlhost'
app.config['MYSQL_USER'] = 'mysqluser'
app.config['MYSQL_PASSWORD'] = 'mysqlpass'
app.config['MYSQL_DB'] = 'dbmysql'
app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672//'
app.config['CELERY_BACKEND'] = 'db+mysql://mysqluser:mysqlpass@mysqlhost/dbmysql'
app.config['CELERY_ACCEPT_CONTENT'] = ['json']
app.config['CELERY_TASK_SERIALIZER' ]= 'json'
app.config['CELERY_RESULT_SERIALIZER'] = 'json'

celery = make_celery(app)

mysql = MySQL(app)

# CONEXÃO COM O AD
def conn():
    server_name = 'adserver'
    user_name   = 'CN=usersvc,OU=Contas de Servico,DC=mdh,DC=gov,DC=br'
    password    = 'passsvc'
    server      = Server(server_name, get_info=ALL)
    conn        = Connection(server, user=user_name, password=password)
    c           = conn.bind()
    return conn

# REGRAS DE AUTENTICAÇÃO PARA PÁGINA DE LOGIN
@app.route('/', methods=['GET','POST'])
def index():

	if request.method == 'POST':
		session.pop('username', None)

		usernameForm = request.form['username']
		domain_name = 'mdh.gov.br'
		domain      = domain_name.split('.')
		connect     = conn()

		try:
			connect.search('dc={},dc={},dc={}'.format(domain[0], domain[1], domain[2]), '(sAMAccountName={})'.format(usernameForm), attributes = [ 'cn' ], search_scope=SUBTREE )
			obj  = connect.entries[0].cn.value
			cn = str(obj)

			passwordForm = request.form['password']
			serverAd = 'adserver'
			userNameConn = 'CN={},OU=ADM,OU=N3,OU=HEPTA,DC=mdh,DC=gov,DC=br'.format(cn)
			passwordAdConn = passwordForm
			serverAdConn      = Server(serverAd, get_info=ALL)
			connAd        = Connection(serverAdConn, user=userNameConn, password=passwordAdConn)
			cAd =  connAd.bind()

			if cAd == True:
				session['username'] = request.form['username']
				return redirect(url_for('usuarios'))
			else:
				return redirect(url_for('index'))

			return jsonify({'Conn': cAd}), 200

		except Exception as error_message:
			return redirect(url_for('index'))

	return render_template('index.html')

@app.route('/usuarios')
def usuarios():
	if g.username:
		try:
			cur = mysql.connection.cursor()
			cur.execute("SELECT * FROM users")
			data = cur.fetchall()
			cur.close()

			user = g.username

			domain_name = 'mdh.gov.br'
			domain      = domain_name.split('.')
			connect     = conn()

			connect.search('dc={},dc={},dc={}'.format(domain[0], domain[1], domain[2]), '(sAMAccountName={})'.format(user), attributes = [ 'sAMAccountName', 'distinguishedName', 'displayName'], search_scope=SUBTREE )

			displayNameObj  = connect.entries[0].displayName.value
			displayName = str(displayNameObj)

			return render_template('usuarios.html', users=data, dataname=[{'displayName': displayName}])

		except Exception as e:
			return redirect(url_for('index'))

	return redirect(url_for('index'))

	
@app.route('/insert', methods=['POST'])
def insert():

	login = str(request.json.get('login', None))
	vinculo = str(request.json.get('vinculo', None))
	cargo = str(request.json.get('cargo', None))
	siape = str(request.json.get('siape', None))
	cpf = str(request.json.get('cpf', None))
	sala = str(request.json.get('sala', None))
	ramal = str(request.json.get('ramal', None))
	created_at = str(request.json.get('created_at', None))

	insertTask.delay(login, vinculo, cargo, siape, cpf, sala, ramal, created_at)

	return 'Celery Executado'



@celery.task(name='app.insertTask')
def insertTask(login, vinculo, cargo, siape, cpf, sala, ramal, created_at):
	# if request.method == 'POST':
		# flash("Data Inserted Sucessfully")

	try:
		if siape == "<not set>":
			siape = "Não possui"
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users (login, vinculo, cargo, siape, cpf, sala, ramal, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (login, vinculo, cargo, siape, cpf, sala, ramal, created_at))
		mysql.connection.commit()

		#return jsonify({'login': login}), 200
		return 'Usuario Inserido'

	except Exception as e:
		return 'Error'
	finally:
		cur.close()


		# return redirect(url_for('usuarios'))


@app.route('/delete/<string:id_data>', methods=['POST', 'GET'])
def delete(id_data):

	domain_name = 'mdh.gov.br'
	domain      = domain_name.split('.')
	connect     = conn()

	try:
		# cur = mysql.connection.cursor()
		# cur.execute("DELETE FROM users WHERE id = {}".format(id_data))
		# mysql.connection.commit()

		cur = mysql.connection.cursor()
		cur.execute("SELECT login FROM users WHERE id = {}".format(id_data))
		data = cur.fetchone()
		cur.execute("DELETE FROM users WHERE id = {}".format(id_data))
		mysql.connection.commit()

		data_s = str(data)
		chars = ")(,'"

		for char in chars:
			data_s = data_s.replace(char, "")

		connect.search('dc={},dc={},dc={}'.format(domain[0], domain[1], domain[2]), '(sAMAccountName={})'.format(data_s), attributes = [ 'distinguishedName' ], search_scope=SUBTREE )
		distinguishedNameObj  = connect.entries[0].distinguishedName.value
		distinguishedName = str(distinguishedNameObj)

		notSet = '<not set>'

		connect.modify(distinguishedName, {'extensionAttribute15':  [(MODIFY_REPLACE, [str(notSet)])]})

		return redirect(url_for('usuarios'))
	except Exception as e:
		return jsonify(e), 400
	finally:
		cur.close()

@app.route('/download', methods=['POST', 'GET'])
def download():
    def generate():
        data = StringIO()
        w = csv.writer(data, delimiter=';')

        # write header
        w.writerow(('Id', 'Login', 'Vinculo', 'Cargo', 'Siape', 'Cpf', 'Sala', 'Ramal', 'Atualizado Em'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        data_user = cur.fetchall()

        data_user_l = list(data_user)

        # write each data_user_l item
        for item in data_user_l:
            w.writerow((
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
                item[5],
                item[6],
				item[7],
                item[8],
                item[9].isoformat()  # format datetime as string
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    # add a filename
    headers = Headers()
    headers.set('Content-Disposition', 'attachment', filename='usuarios.csv')

    # stream the response as the data is generated
    return Response(
        stream_with_context(generate()),
        mimetype='text/csv', headers=headers
    )

@app.route('/user',methods=['POST'])
def user():

	login = str(request.json.get('login', None))

	domain_name = 'mdh.gov.br'
	domain      = domain_name.split('.')
	connect     = conn()

	try:
		connect.search('dc={},dc={},dc={}'.format(domain[0], domain[1], domain[2]), '(sAMAccountName={})'.format(login), attributes = [ 'extensionAttribute15' ], search_scope=SUBTREE )
		obj  = connect.entries[0].extensionAttribute15.value
		extensionAttribute15 = str(obj)


		# cur = mysql.connection.cursor()
		# cur.execute("SELECT login FROM users WHERE login = '{}'".format(login))
		# data = cur.fetchone()
		# data_s = str(data)
		# chars = ")(,'"

		# for char in chars:
		# 	data_s = data_s.replace(char, "")
		
		if extensionAttribute15 == 'True':
			return 'True'
		else:
			return 'False'

	except Exception as e:
		return jsonify(e), 200


# REGRA PARA PÁGINA DE LOGOUT
@app.route("/logout", methods=['GET','POST'])
def logout():
	if 'username' in session:
		g.username = None
		dropsession()

		return redirect(url_for('index'))

	return 'Not logged in'

@app.before_request
def before_request():
	g.username = None
	if 'username' in session:
		g.username = session['username']

@app.route('/getsession')
def getsession():
	if 'username' in session:
		return session['username']

	return 'Not logged in'

@app.route('/dropsession')
def dropsession():
	session.pop('username', None)
	return 'Dropped!'


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port='5000')