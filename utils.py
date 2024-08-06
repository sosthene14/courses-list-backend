from flask import  request, jsonify

import jwt
import datetime
from bson import ObjectId
import os
import random
import random
import base64
from Emailer.core import EmailSender
from dotenv import load_dotenv
load_dotenv()

HOST_USER = os.environ.get('HOST_USER')
HOST_PASSWORD = os.environ.get('HOST_PASSWORD')
sender = EmailSender(HOST_USER, HOST_PASSWORD)


def check_user_verified(user):
    try:
        print(user)
        if user['isVerified']:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
    
def send(receiver, subject, html_file_path, context):  
    return sender.send(
  receiver=receiver,
  subject=subject,
  template=html_file_path,
  context=context,
)


def generate_otp_code():
    code = ''.join(random.choices('0123456789', k=6))
    return code


def send_email_verification(otp_code,user_mail,subject,html_file_path,username=None,ad_id=None):
    html_file_path = html_file_path # <h1>Hey {{ name }}<h1>
    context = {'validation_code': otp_code,'username':username,'ad_id':ad_id} # The value of variable in html {{ name }}
    receiver = user_mail
    subject = subject 
    send(receiver, subject, html_file_path, context)
    return jsonify({'message': 'Email sent successfully'})


def format_mongodb_dates(data):
    # Vérifier chaque clé dans les données
    for key, value in data.items():
        if isinstance(value, dict) and '$date' in value:
            # Si la valeur est un dictionnaire avec une clé '$date', formater la date
            date_str = value['$date']
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            data[key] = date_obj.strftime('%d/%m/%Y')
        elif isinstance(value, dict):
            # Si la valeur est un dictionnaire, récursivement appliquer la fonction
            format_mongodb_dates(value)
        elif isinstance(value, list):
            # Si la valeur est une liste, appliquer la fonction à chaque élément de la liste
            for item in value:
                format_mongodb_dates(item)
    
    return data

def increment_total_ads(user,users_collection,field):
    try:
        if users_collection.update_one({"_id": ObjectId(user['_id'])}, {"$inc": {field: 1}}):
            return True
        else:
            return False
    except Exception as e:
        return False
    

def process_dates(data):
        """Convert date fields in the data dictionary."""
        date_fields = ["arrivalDate", "departureDate", "expirationDate", "publicationDate"]
        for field in date_fields:
            if field in data:
                data[field] = convert_dates(data[field])
        return data

def decrement_total_ads(user,users_collection,field):
    try:
        if users_collection.update_one({"_id": ObjectId(user['_id'])}, {"$inc": {field: -1}}):
            return True
        else:
            return False
    except Exception as e:
        return False


def parse_iso_date(date_str):
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")
    
def convert_dates(date_string):
    try:
        date_object = datetime.datetime.fromisoformat(date_string)
        date_utc = date_object.astimezone(datetime.timezone.utc)
        return date_utc
    except ValueError as e:
        print("Erreur de conversion :", e)
        return None
    
def make_user_verified(user,users_collection):
    try:
        if users_collection.update_one({"_id": ObjectId(user['_id'])}, {"$set": {"isVerified": True}}):
            return True
        else:
            return False
    except Exception as e:
        return False
    
def add_otp_code(user,html_file_path,users_collection):
    try:
        if not 'attempts' in user  or user['attempts'] < 5 :
            otp_code = generate_otp_code()
            update_attempts = user['attempts'] + 1 if 'attempts' in user else 1
            if users_collection.update_one({"_id": ObjectId(user['_id'])}, {"$set": {"otp_code": otp_code,"attempts": update_attempts, "otp_code_expiration": datetime.datetime.now() + datetime.timedelta(minutes=15)}}):
                send_email_verification(otp_code,user['email'], "ROCOLIS - CODE DE VERIFICATION", html_file_path,user['firstName'])
                return jsonify({"response": True,"message": "Code envoyé"}), 200
        else:
            return jsonify({"response": False,"message": "Trop de tentatives, veuillez reessayer plus tard"}), 400
    except Exception as e:
        return jsonify({"response": False, "error": str(e),"message": "Une erreur est survenue"}),500

def check_otp_code(user, otp_code):
    try:
        if user['otp_code'] == otp_code:
            if user['otp_code_expiration'] > datetime.datetime.now():
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        return False

def return_mail_using_id(id,travel_collection,users_collection):
    try:
        user = travel_collection.find_one({'_id': ObjectId(id)})
        if user:
            email = users_collection.find_one({'_id': ObjectId(user['publishedBy'])})
            if email:
                return email['email']
            else:
                return None
        else:
            return None
    except Exception as e:
        return None
    
def compare_travel_and_parcel(travel_collection,parcel_collection,travel_id,parcel_id):
    try:
        travel = travel_collection.find_one({'_id': ObjectId(travel_id)})
        parcel = parcel_collection.find_one({'_id': ObjectId(parcel_id)})
        if travel and parcel:
            if travel["departureCity"] == parcel["departureCity"] and travel["destinationCity"] == parcel["destinationCity"] and travel["departureCountry"] == parcel["departureCountry"] and travel["destinationCountry"] == parcel["destinationCountry"]:
                if travel["availableKilos"] >= parcel["availableKilos"]:
                    pass
                else:
                    return jsonify({"response": False, "message": "Le nombre de kilos disponibles est insuffisant"}), 400
            else:
                return jsonify({"response": False, "message": "La ville de départ ou d'arrivée présente sur le colis, ne correspond pas à celui du voyageur"}), 400
        else:
            return jsonify({"response": False, "message": "Le colis ou le voyageur n'existe pas"}), 400
    except Exception as e:
        return jsonify({"response": False, "message": str(e)}), 500
    
def check_traveler_ad_id_validiation(id,travel_collection):
    try:
        user = travel_collection.find_one({'_id': ObjectId(id)})
        if user:
            return True
        else:
            return False
    except Exception as e:
        return False
    
def return_sub_using_email(email,users_collection):
    try:
        user = users_collection.find_one({'email': email})
        if user:
            return str(user['_id'])
        else:
            return None
    except Exception as e:
        return None

def check_user_google(user):
    try:
        if user['isGoogle']:
            return True
        else:
            return False
    except Exception as e:
        return False

def get_user_name(user):
    try:
        if user['firstName']:
            return user['firstName']
        else:
            return None
    except Exception as e:
        return None
    
def check_user_banned(user):
    try:
        if user['isbanned']:
            return True
        else:
            return False
    except Exception as e:
        return False
    
def check_email_exists(email,users_collection):
    try:
        user = users_collection.find_one({'email': email})
        if user:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def update_acces_refresh_tokens(sub, access_token, refresh_token, users_collection):
    try:
        users_collection.update_one({"_id": ObjectId(sub)}, {"$set": {"access_token": access_token, "refresh_token": refresh_token}})
        return True
    except Exception as e:
        return False
    
def generate_secret_key():
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')

def generate_secret_key_refresh():
    return base64.urlsafe_b64encode(os.urandom(128)).decode('utf-8')

def check_google_user(user):
    try:
        if user['isGoogle']:
            return True
        else:
            return False
    except Exception as e:
        return False

def generate_access_token(sub, secret_key):
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    token = jwt.encode({"sub": sub, "exp": expiration_time}, secret_key, algorithm="HS256")
    return token

def generate_refresh_token(sub, secret_key):
    try:
        payload = {
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=720),
            'sub': sub,
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    except Exception as e:
        return str(e)

def getAuthorizationToken():
    try:
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split('Bearer ')[1]
            return token
    except Exception as e:
        return None
    

def verify_refresh_token(refresh_token, SECRET_KEY):
    try:
        return jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
    except Exception as e:
        return None
def verify_access_token(access_token, SECRET_KEY):
    try:
        return jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
    except Exception as e:
        return None
    

def delete_otp_code(user,users_collection):
    try:
        users_collection.update_one(
            {"_id": ObjectId(user['_id'])},
            {"$unset": {"otp_code": "", "otp_code_expiration": ""}, "$set": {"attempts": 0}}
        )
        return True
    except Exception as e:
        return False

def get_traveler_details(user_id,users_collection):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return {'created':user['created'],'name':user['name'],'firstName':user['firstName'],'isVerified':user['isVerified']}
    except Exception as e:
        return None
    

def update_ad_view(ad_id, ad_collection):
    try:
        result = ad_collection.update_one(
            {"_id": ObjectId(ad_id)},
            {"$inc": {"viewNumber": 1}}
        )
        return result.modified_count > 0
    except Exception as e:
        return False
    

def is_valid_ids(id1, id2,id3,evaluations_collection):
    try:
        evaluation = evaluations_collection.find_one({"evaluationId1": id1, "evaluationId2": id2, "evaluationId3": id3})
        if evaluation and evaluation["haveSeenEvaluation"] == False:
            return {"response": True,"data": evaluation}
        else:
            return {"response": False,"data": None}
    except Exception as e:
        return  {"response": False,"data": None}
