#IBM bluemix app env variables of the app
import os
import swiftclient
import keystoneclient
import pyDes
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
auth_url = ""
password = ""
project_id = ""
region_name = ""
user_id = ""

# Initialize the Flask application
k = pyDes.des(b"DESCRYPT", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

global conn 
conn = swiftclient.client.Connection(key=password,
	authurl=auth_url,
	auth_version='3',
	os_options={"project_id": project_id,
	"user_id": user_id,
	"region_name": region_name
	})

#UPLOAD_FOLDER = '/'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
	global list_of_files
	list_of_files = []
	
	for container in conn.get_account()[1]:                    
		for data in conn.get_container(container['name'])[1]:
			list_of_files.append(format(data['name']))
				
	return render_template("index.html", list_of_files = list_of_files)

@app.route("/upload", methods = ['POST'])
def upload():
	#file to upload
	if request.form.get('add', None) == "file":
		print "Shit"
	
	else :	
		file = request.files['file_to_upload']
		file_name = file.filename
		file_name = secure_filename(file_name)
		content = file.read() 
		#file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
		
		#get the size of the file
		file.seek(0, os.SEEK_END)
		size_of_file = file.tell()
		print size_of_file

		#create container
		container = conn.put_container('new_container')
			
		if (size_of_file<=1000000) :
			#encrypt file
			encrypted_file = k.encrypt(content)
			#upload encrypted file
			conn.put_object("new_container", file_name, contents = encrypted_file, content_type='')
		
	return redirect("/")

@app.route("/download", methods = ['POST'])
def download():

	file_name = request.form['file_to_download']
	#to download
	
	obj = conn.get_object("new_container", file_name,resp_chunk_size=None, query_string=None)

	#print obj[1]
	file_content_bytes = obj[1]

	#decryption
	file_contents = k.decrypt(file_content_bytes).decode('UTF-8')

	end = str(file_contents).index('\n')

	print_message = str(file_contents)[0:end]
	return render_template("/index.html", print_message = "First line = " + print_message, list_of_files=list_of_files)
	
@app.route("/delete", methods = ['POST'])
def delete():

	file = request.form['file_to_delete']
	conn.delete_object("new_container", file)
	return redirect("/")

port = os.getenv('PORT', '8000')
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(port))


'''if __name__ == "__main__":
	app.run()'''
