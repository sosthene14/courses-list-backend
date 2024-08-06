from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient
import datetime
from flask_cors import CORS
from flask_compress import Compress
from dotenv import load_dotenv
import os
from bson import json_util,ObjectId
from flask import after_this_request
from mailServer import EmailSender
from mailsTemplates import validation_message_group
load_dotenv()

SECRET_KEY = os.environ.get("SECRET")
MONGOURI = os.environ.get("MONGOURI")
DBNAME = os.environ.get("DBNAME")
ORACLECOLLECTIONNAME = os.environ.get("ORACLECOLLECTIONNAME")
NOSQLCOLLECTIONNAME = os.environ.get("NOSQLCOLLECTIONNAME")
LARAVELCOLLECTIONNAME = os.environ.get("LARAVELCOLLECTIONNAME")
USERSCOLLECTIONNAME = os.environ.get("USERSCOLLECTIONNAME")

CLIENT = MongoClient(MONGOURI)
db = CLIENT[DBNAME]
oracle_collection = db[ORACLECOLLECTIONNAME]
nosql_collection = db[NOSQLCOLLECTIONNAME]
laravel_collection = db[LARAVELCOLLECTIONNAME]
HOST_USER = os.environ.get('HOST_USER')
HOST_PASSWORD = os.environ.get('HOST_PASSWORD')

app = Flask(__name__)
CORS(app)
Compress(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['REFRESH_TOKEN_EXPIRATION'] = datetime.timedelta(days=30)




"""********************************************Add ads ***************************************************"""

@app.route('/api/v1/upload-group', methods=['POST'])
def upload_group():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        print(data)
        course_type = data.get('courseType', None)
        print(course_type)
        if not course_type:
            return jsonify({'message': 'Course type is required'}), 400

        collection = None
        if course_type == 'oracle':
            collection = oracle_collection
        elif course_type == 'nosql':
            collection = nosql_collection
        elif course_type == 'laravel':
            collection = laravel_collection

        if collection is None:
            return jsonify({'message': 'Collection not found'}), 400

        del data['courseType']
        collection.insert_one(data)
        return jsonify({'message': "success"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': str(e)}), 500


@app.route('/api/v1/get-groups/<string:course>', methods=['GET'])
def get_groups(course):
    try:
        if course == 'oracle':
            collection = oracle_collection
        elif course == 'nosql':
            collection = nosql_collection
        elif course == 'laravel':
            collection = laravel_collection
        if collection is None:
            return jsonify({'message': 'Collection not found'}), 400
        groups = collection.find()
        result = json_util.dumps({'data': list(groups)}), 200
        return result
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': str(e)}), 500
        

@app.route("/api/v1/add-student-to-group", methods=["POST"])
def add_user():
    try:
        data = request.json
        course_type = data["courseType"]
        collection = None

        # Choisir la collection en fonction du type de cours
        if course_type == "oracle":
            collection = oracle_collection
        elif course_type == "nosql":
            collection = nosql_collection
        elif course_type == "laravel":
            collection = laravel_collection
        
        # Si aucune collection n'est trouvée
        if collection is None:
            return jsonify({"message": "Collection not found"}), 400
        
        # Convertir l'_id en ObjectId si nécessaire
        object_id = ObjectId(data["_id"])
        
        # Suppression du champ courseType pour ne pas le stocker dans le document
        del data["courseType"]
        del data["_id"]

        result = collection.find_one({"_id": object_id})
        if result:
            # Ajouter l'utilisateur au groupe existant en utilisant $push
            collection.update_one(
                {"_id": object_id},
                {"$push": {"groupe": data}}
            )
            return jsonify({"message": "User added successfully"}), 200
        else:
            return jsonify({"message": "Group not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": str(e)}), 500

@app.route("/api/v1/delete-user", methods=["POST"])
def delete_user_from_group():
    try:
        data = request.json
        student_index = data["indexStudent"]
        course_type = data["courseType"]
        collection = None

        # Choisir la collection en fonction du type de cours
        if course_type == "oracle":
            collection = oracle_collection
        elif course_type == "nosql":
            collection = nosql_collection
        elif course_type == "laravel":
            collection = laravel_collection
        
        # Si aucune collection n'est trouvée
        if collection is None:
            return jsonify({"message": "Collection not found"}), 400
        
        # Convertir l'_id en ObjectId si nécessaire
        object_id = ObjectId(data["_id"])

        # Rechercher le document correspondant à l'_id
        result = collection.find_one({"_id": object_id})
        if result:
            # Première étape : utiliser $unset pour effacer l'élément à l'index donné
            collection.update_one(
                {"_id": object_id}, 
                {"$unset": {f"groupe.{student_index}": 1}}
            )

            # Deuxième étape : utiliser $pull pour retirer les éléments 'null'
            collection.update_one(
                {"_id": object_id},
                {"$pull": {"groupe": None}}
            )

            return jsonify({"message": "User deleted successfully"}), 200
        
        return jsonify({"message": "Document not found"}), 404
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": str(e)}), 500

"""********************************************affectation***************************************************"""

@app.route('/index', methods=['GET'])
def html_return():
    return render_template('index.html')

@app.route('/', methods=['GET'])
def running():
    return jsonify({'message': 'rocolis backend is running'}), 200
    
if __name__ == '__main__':
    app.run(debug=True)