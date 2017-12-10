from flask import Flask, render_template, request, redirect
import os

from core.dbdriver import get_db, init_tables
from core import redisdriver
import redis
from datetime import datetime



class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

app = Flask(__name__)


# Init tables in db
init_tables()

"""
Index page
Show list of `asks`, and cheer count of each ask
"""
@app.route('/')
def index():
	
	client = redisdriver.get_client()

	#ret = client.set('test:string1', 'test...', 20)
	#print(ret.get_result())
	#assert ret.get_result() == True

	#ret = client.get('test:string1')
	#print(ret.get_result())
	#assert ret.get_result() == 'test...'

	success = True
	cache = client.lrange('askhy:asktable_', 0, -1)

	#print(cache)

	if not cache :
		success = False

	else :
		#print(bcolors.OKGREEN + "Cache hit!" + bcolors.ENDC)
		#print(cache)

		result = []

		from datetime import datetime

		for row in cache :
			item = row.decode().split("/")
			#print(item)
			result.append((
				int(item[0]), # id
				item[1], # message
				item[2], # ip_address
				datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S'), # register_time
				int(item[4]), # cheer_cnt
			))

	#cache = set()
	if not success :
		cache = []

		with get_db().cursor() as cursor :
			#print(bcolors.WARNING + "Cache not exists. Create cache" + bcolors.ENDC)

			#print(ret)

			cursor.execute("SELECT *, (SELECT COUNT(*) FROM `cheer` WHERE ask_id = ask.id) AS cheer_cnt FROM `ask`")
			
			result = cursor.fetchall()
			#cache2 = list(result)
			#print(bcolors.OKGREEN + str(len(result)) + bcolors.ENDC)

			for item in result:
				#print(item)

				data = "%s/%s/%s/%s/%s" % (
					str(item[0]), # id
					item[1], # message
					item[2], # ip_address
					item[3].strftime("%Y-%m-%d %H:%M:%S"), # register_time
					str(item[4]), # cheer_cnt
				)

				#print(bcolors.OKGREEN + data + bcolors.ENDC)

				finish = client.lpush('askhy:asktable_', data)
				#print(finish)



	return render_template('main.html',
		dataset=result,
	)


"""
Show detail of one `ask`
See all cheers in this ask
"""
@app.route('/ask/<int:ask_id>', methods=['GET'])
def view_ask(ask_id):
	conn = get_db()

	with conn.cursor() as cursor :
		cursor.execute("SELECT * FROM `ask` WHERE id = %s", (ask_id, ))
		row = cursor.fetchone()

		cursor.execute("SELECT * FROM `cheer` WHERE ask_id = %s", (ask_id, ))
		rows2 = cursor.fetchall()

	return render_template('detail.html',
		id=row[0],
		message=row[1],
		ip_address=row[2],
		register_time=row[3],
		current_url=request.url,
		cheers=rows2,
	)


"""
Add new ask

[request params]
  - message
"""
@app.route('/ask', methods=['POST'])
def add_ask():
	conn = get_db()
	message = request.form.get('message')

	with conn.cursor() as cursor :
		sql = "INSERT INTO `ask` (`message`, `ip_address`) VALUES (%s, %s)"
		r = cursor.execute(sql, (message, request.remote_addr))

	id = conn.insert_id()
	conn.commit()

	with conn.cursor() as cursor :

		cursor.execute("SELECT * FROM `ask` WHERE id = %s", (id, ))
		item = cursor.fetchone()
		client = redisdriver.get_client()
		#print(item)

		data = "%s/%s/%s/%s/%s" % (
		str(item[0]), # id
		item[1], # message
		item[2], # ip_address
		item[3].strftime("%Y-%m-%d %H:%M:%S"), # register_time
		str(0), # cheer_cnt
		)
		#print(bcolors.OKGREEN + data + bcolors.ENDC)

		client.lpush('askhy:asktable_', data)
		#print(finish)


	return redirect("/#a" + str(id))


"""
Add new cheer

[request params]
  - ask_id
  - message
"""
@app.route('/cheer', methods=['POST'])
def add_cheer():
	conn = get_db()
	ask_id = request.form.get('ask_id')
	message = request.form.get('message')

	with conn.cursor() as cursor :
		sql = "INSERT INTO `cheer` (`ask_id`, `message`, `ip_address`) VALUES (%s, %s, %s)"
		r = cursor.execute(sql, (ask_id, message, request.remote_addr))

	conn.commit()

	back = request.form.get('back')
	if back :
		return redirect(back)
	else :
		return redirect("/#c" + ask_id)


"""
Template filter: <hide_ip_address>
Hide last sections of IP address

ex) 65.3.12.4 -> 65.3.*.*
"""
@app.template_filter()
def hide_ip_address(ip_address):
	if not ip_address : return ""
	else :
		ipa = ip_address.split(".")
		return "%s.%s.*.*" % (ipa[0], ipa[1])




if __name__ == '__main__':
	app.run(
		host='0.0.0.0',
		debug=True,
		port=os.environ.get('APP_PORT', 8080)
	)
