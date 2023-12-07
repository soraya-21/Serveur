from flask import Flask
from flask_pymongo import pymongo
from flask_cors import CORS
from flask import Flask, request, jsonify, session
from bson import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.secret_key = "your-secret-key"
app.config["UPLOAD_FOLDER"] = "static/img"

CONNECTION_STRING = "mongodb+srv://fiesta:fiestadatabase@cluster0.uggrezt.mongodb.net/"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database("cluster0")


class User:
    def __init__(
        self,
        nom,
        prenoms,
        adresse,
        telephone,
        email,
        a_propos,
        liens_reseaux_sociaux,
        photo,
        experience,
        date_de_naissance,
        education,
        profession,
        _id=None,
    ):
        self.nom = nom
        self.prenoms = prenoms
        self.adresse = adresse
        self.telephone = telephone
        self.email = email
        self.a_propos = a_propos
        self.liens_reseaux_sociaux = liens_reseaux_sociaux
        self.experience = experience
        self.date_de_naissance = date_de_naissance
        self.education = education
        self.profession = profession
        self.photo = photo
        self._id = _id

    def save(self):
        user_data = {
            "nom": self.nom,
            "prenoms": self.prenoms,
            "adresse": self.adresse,
            "telephone": self.telephone,
            "email": self.email,
            "a_propos": self.a_propos,
            "liens_reseaux_sociaux": self.liens_reseaux_sociaux,
            "experience": self.experience,
            "date_de_naissance": self.date_de_naissance,
            "education": self.education,
            "profession": self.profession,
        }

        if self.photo:
            filename = secure_filename(self.photo.filename)
            photo_path = app.config["UPLOAD_FOLDER"] + "/" + filename
            self.photo.save(photo_path)
            user_data["photo"] = photo_path

        result = db.members.insert_one(user_data)
        self._id = result.inserted_id

    @classmethod
    def find_by_id(cls, user_id):
        user_data = db.members.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return cls(**user_data)
        return None


@app.route("/api/register_members", methods=["POST"])
def register():
    nom = request.form.get("Nom")
    prenoms = request.form.get("Prénoms")
    adresse = request.form.get("Adresse")
    telephone = request.form.get("Téléphone")
    email = request.form.get("Email")
    a_propos = request.form.get("A propos")
    liens_reseaux_sociaux = request.form.get("Liens réseaux sociaux")
    photo = request.files.get("Photo")
    experience = request.files.get("Expérience")
    date_de_naisssance = request.files.get("Date de naissance")
    education = request.files.get("Education")
    profession = request.files.get("Profession")

    user_exists = db.members.find_one({"nom": nom, "prenoms": prenoms})
    if user_exists:
        return (
            jsonify({"message": "User already exists"}),
            409,
        )

    new_user = User(
        nom,
        prenoms,
        adresse,
        telephone,
        email,
        a_propos=a_propos,
        liens_reseaux_sociaux=liens_reseaux_sociaux,
        photo=photo,
        experience=experience,
        date_de_naissance=date_de_naisssance,
        education=education,
        profession=profession,
    )
    new_user.save()

    return jsonify({"message": "Registration successful", "user_id": str(new_user._id)})


@app.route("/api/get_member/<string:user_id>", methods=["GET"])
def get_member(user_id):
    user = User.find_by_id(user_id)
    if user:
        user_info = {
            "Nom": user.nom,
            "Prénoms": user.prenoms,
            "Adresse": user.adresse,
            "Téléphone": user.telephone,
            "Email": user.email,
            "A propos": user.a_propos,
            "Liens réseaux sociaux": user.liens_reseaux_sociaux,
            "Photo": user.photo,
            "experience": user.experience,
            "date_de_naissance": user.date_de_naissance,
            "education": user.education,
            "profession": user.profession,
        }
        return jsonify(user_info)
    else:
        return jsonify({"message": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
