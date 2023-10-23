from http.client import NOT_FOUND
import os
from flask import Flask, jsonify,request, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'files'

db = SQLAlchemy(app)

upload_folder = 'files'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

class FileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)

    def __init__(self, filename, file_size):
        self.filename = filename
        self.file_size = file_size

with app.app_context():
    db.create_all() 

@app.route('/upload-file', methods=['POST'])
def upload_file():
    uploaded_files = request.files.getlist('files')
    for file in uploaded_files:
        if file:
            if file.filename == '':
                return 'No selected file', 400
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_size = len(file.read()) 

            file_metadata = FileMetadata(filename=filename, file_size = file_size)
            db.session.add(file_metadata)


    db.session.commit()

    return jsonify({'message': 'Files uploaded successfully'})

@app.route('/get_all_files', methods=['GET'])
def get_all_files():
    files = FileMetadata.query.all()
    file_list = [
        {
            'id': file.id,
            'filename': file.filename,
            'file_size': file.file_size
        }
        for file in files
    ]
    return jsonify(file_list)

@app.route('/get-file/<int:file_id>', methods=['GET'])
def get_file(file_id):
    file_metadata = FileMetadata.query.get(file_id)

    if file_metadata:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_metadata.filename)
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=False,  
        )
    else:
        return 'File not found', 404
   
if __name__ == '__main__':
    app.run(host='0.0.0.0', port= 5000, debug=True)
