# Music Voting App

This document outlines the database design for the Music Voting App.

## Database Design

The application uses a relational database to manage users, albums, and songs, along with the voting relationships between users and musical items. The database schema is defined using Flask-SQLAlchemy, with the models located in `backend/app/models.py`.

### ERD Model Information

Here's a breakdown of the entities and their relationships:

#### Entities:

1.  **User**
    *   `id`: Primary Key, Integer. Unique identifier for the user.
    *   `username`: String (80 characters), Unique, Not Null. The user's chosen username for login.
    *   `password_hash`: String (128 characters), Not Null. Stores the hashed password for security.
    *   `is_admin`: Boolean, Default: False, Not Null. Indicates if the user has administrative privileges.

2.  **Album**
    *   `id`: Primary Key, Integer. Unique identifier for the album.
    *   `title`: String (120 characters), Not Null. The title of the album.
    *   `artist`: String (120 characters), Not Null. The artist(s) of the album.
    *   `cover_image_url`: String (255 characters). Optional URL to the album's cover image.

3.  **Song**
    *   `id`: Primary Key, Integer. Unique identifier for the song.
    *   `title`: String (120 characters), Not Null. The title of the song.
    *   `album_id`: Foreign Key, Integer, Not Null. Links the song to its parent album (`Album.id`).

#### Relationships:

1.  **User to Album (Many-to-Many - `album_votes` association table)**
    *   A user can vote for multiple albums.
    *   An album can be voted for by multiple users.
    *   **Association Table: `album_votes`**
        *   `user_id`: Foreign Key (`User.id`), Primary Key (composite).
        *   `album_id`: Foreign Key (`Album.id`), Primary Key (composite).

2.  **User to Song (Many-to-Many - `song_votes` association table)**
    *   A user can vote for multiple songs.
    *   A song can be voted for by multiple users.
    *   **Association Table: `song_votes`**
        *   `user_id`: Foreign Key (`User.id`), Primary Key (composite).
        *   `song_id`: Foreign Key (`Song.id`), Primary Key (composite).

3.  **Album to Song (One-to-Many)**
    *   An album can have multiple songs.
    *   A song belongs to exactly one album.
    *   The `album_id` in the `Song` table establishes this relationship. When an album is deleted, all associated songs are also deleted (cascade="all, delete-orphan").

### Visual Representation (Conceptual ERD)

![HW2 ERD](./HW2-ERD.png)

This ERD (Entity-Relationship Diagram) illustrates how the different tables are connected and how data flows within the application.
