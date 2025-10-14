from flask import Blueprint, request, jsonify
from .models import db, User, Album, Song
from .extensions import bcrypt
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from functools import wraps

main = Blueprint("main", __name__)


# Custom decorator for admin-only routes
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("is_admin"):
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper


@main.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Username already exists"}), 409

        # First registered user becomes an admin
        is_first_user = User.query.count() == 0
        new_user = User(username=username, is_admin=is_first_user)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User created successfully"}), 201

    except Exception as e:
        # If any error happens, print it to the Flask terminal
        print(f"An error occurred in the register route: {e}")
        # And send a proper JSON error response back to the browser
        return jsonify(
            {"msg": "An internal server error occurred.", "error": str(e)}
        ), 500


@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        additional_claims = {"is_admin": user.is_admin}
        access_token = create_access_token(
            identity=str(user.id), additional_claims=additional_claims
        )
        return jsonify(
            access_token=access_token,
            user={"id": user.id, "username": user.username, "isAdmin": user.is_admin},
        )

    return jsonify({"msg": "Bad username or password"}), 401


@main.route("/profile")
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(id=user.id, username=user.username, isAdmin=user.is_admin), 200


@main.route("/albums", methods=["POST"])
@admin_required()
def add_album():
    data = request.get_json()
    new_album = Album(
        title=data["title"],
        artist=data["artist"],
        cover_image_url=data.get("cover_image_url"),
    )
    db.session.add(new_album)
    db.session.commit()
    return jsonify({"msg": "Album added successfully", "id": new_album.id}), 201


@main.route("/albums/<int:album_id>/songs", methods=["POST"])
@admin_required()
def add_song(album_id):
    data = request.get_json()
    new_song = Song(title=data["title"], album_id=album_id)
    db.session.add(new_song)
    db.session.commit()
    return jsonify({"msg": "Song added successfully", "id": new_song.id}), 201


@main.route("/albums", methods=["GET"])
def get_albums():
    albums = Album.query.all()
    output = []
    for album in albums:
        album_data = {
            "id": album.id,
            "title": album.title,
            "artist": album.artist,
            "cover_image_url": album.cover_image_url,
            "vote_count": len(album.voters),
        }
        output.append(album_data)
    return jsonify(output)


@main.route("/albums/<int:album_id>/songs", methods=["GET"])
def get_songs(album_id):
    songs = Song.query.filter_by(album_id=album_id).all()
    output = []
    for song in songs:
        song_data = {
            "id": song.id,
            "title": song.title,
            "album_id": song.album_id,
            "vote_count": len(song.voters),
        }
        output.append(song_data)
    return jsonify(output)


@main.route("/vote/album/<int:album_id>", methods=["POST"])
@jwt_required()
def vote_album(album_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    album = Album.query.get(album_id)

    if not album:
        return jsonify({"msg": "Album not found"}), 404

    if album in user.voted_albums:
        # User is retrieving/changing their vote, so we remove it
        user.voted_albums.remove(album)
        db.session.commit()
        return jsonify({"msg": "Vote removed"}), 200
    else:
        # Add new vote
        user.voted_albums.append(album)
        db.session.commit()
        return jsonify({"msg": "Voted successfully"}), 200


@main.route("/vote/song/<int:song_id>", methods=["POST"])
@jwt_required()
def vote_song(song_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    song = Song.query.get(song_id)

    if not song:
        return jsonify({"msg": "Song not found"}), 404

    if song in user.voted_songs:
        user.voted_songs.remove(song)
        db.session.commit()
        return jsonify({"msg": "Vote removed"}), 200
    else:
        user.voted_songs.append(song)
        db.session.commit()
        return jsonify({"msg": "Voted successfully"}), 200


@main.route("/my-votes", methods=["GET"])
@jwt_required()
def my_votes():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    voted_album_ids = [album.id for album in user.voted_albums]
    voted_song_ids = [song.id for song in user.voted_songs]
    return jsonify({"voted_albums": voted_album_ids, "voted_songs": voted_song_ids})


# UPDATE an existing album
@main.route("/albums/<int:album_id>", methods=["PUT"])
@admin_required()
def update_album(album_id):
    album = Album.query.get_or_404(album_id)
    data = request.get_json()

    # Update fields if they are provided in the request
    album.title = data.get("title", album.title)
    album.artist = data.get("artist", album.artist)
    album.cover_image_url = data.get("cover_image_url", album.cover_image_url)

    db.session.commit()
    return jsonify({"msg": "Album updated successfully"}), 200


# DELETE an album (and its songs due to cascading delete in the model)
@main.route("/albums/<int:album_id>", methods=["DELETE"])
@admin_required()
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    return jsonify({"msg": "Album deleted successfully"}), 200


# DELETE a song
@main.route("/songs/<int:song_id>", methods=["DELETE"])
@admin_required()
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({"msg": "Song deleted successfully"}), 200


# We can also add a route to get a single album's details for editing
@main.route("/albums/<int:album_id>", methods=["GET"])
def get_album_details(album_id):
    album = Album.query.get_or_404(album_id)
    songs = [
        {"id": song.id, "title": song.title, "vote_count": len(song.voters)}
        for song in album.songs
    ]

    return jsonify(
        {
            "id": album.id,
            "title": album.title,
            "artist": album.artist,
            "cover_image_url": album.cover_image_url,
            "vote_count": len(album.voters),
            "songs": songs,
        }
    ), 200
