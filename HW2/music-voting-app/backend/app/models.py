from .extensions import db, bcrypt

# Association tables for many-to-many relationship (User <-> Vote)
album_votes = db.Table('album_votes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('album_id', db.Integer, db.ForeignKey('album.id'), primary_key=True)
)

song_votes = db.Table('song_votes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    voted_albums = db.relationship('Album', secondary=album_votes, back_populates='voters')
    voted_songs = db.relationship('Song', secondary=song_votes, back_populates='voters')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    cover_image_url = db.Column(db.String(255))
    songs = db.relationship('Song', backref='album', lazy=True, cascade="all, delete-orphan")
    voters = db.relationship('User', secondary=album_votes, back_populates='voted_albums')

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    voters = db.relationship('User', secondary=song_votes, back_populates='voted_songs')