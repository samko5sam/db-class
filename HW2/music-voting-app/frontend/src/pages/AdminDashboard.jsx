import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext.jsx";
import { useNavigate } from "react-router-dom";
import api from "../api/axiosConfig";

const AdminDashboard = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  // State for the list of albums
  const [albums, setAlbums] = useState([]);

  // State for the "Add/Edit Album" modal
  const [isAlbumModalOpen, setIsAlbumModalOpen] = useState(false);
  const [editingAlbum, setEditingAlbum] = useState(null); // null for 'Add', album object for 'Edit'
  const [albumFormData, setAlbumFormData] = useState({
    title: "",
    artist: "",
    cover_image_url: "",
  });

  // State for the "Add Song" modal
  const [isSongModalOpen, setIsSongModalOpen] = useState(false);
  const [songFormData, setSongFormData] = useState({ title: "" });
  const [albumForAddingSong, setAlbumForAddingSong] = useState(null);

  // Fetch all albums on component mount
  const fetchAlbums = async () => {
    try {
      const response = await api.get("/albums");
      const albumsWithDetails = await Promise.all(
        response.data.map((album) => api.get(`/albums/${album.id}`)),
      );
      setAlbums(albumsWithDetails.map((res) => res.data));
    } catch (error) {
      console.error("Failed to fetch albums:", error);
    }
  };

  useEffect(() => {
    if (!user || !user.isAdmin) {
      navigate("/");
    } else {
      fetchAlbums();
    }
  }, [user, navigate]);

  // --- Album Modal Handlers ---
  const openAddAlbumModal = () => {
    setEditingAlbum(null);
    setAlbumFormData({ title: "", artist: "", cover_image_url: "" });
    setIsAlbumModalOpen(true);
  };

  const openEditAlbumModal = (album) => {
    setEditingAlbum(album);
    setAlbumFormData({
      title: album.title,
      artist: album.artist,
      cover_image_url: album.cover_image_url || "",
    });
    setIsAlbumModalOpen(true);
  };

  const handleAlbumFormChange = (e) => {
    const { name, value } = e.target;
    setAlbumFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAlbumSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAlbum) {
        // Update existing album
        await api.put(`/albums/${editingAlbum.id}`, albumFormData);
      } else {
        // Add new album
        await api.post("/albums", albumFormData);
      }
      setIsAlbumModalOpen(false);
      fetchAlbums(); // Refresh list
    } catch (error) {
      console.error("Failed to save album:", error);
      alert("Failed to save album. Check console for details.");
    }
  };

  const handleDeleteAlbum = async (albumId) => {
    if (
      window.confirm(
        "Are you sure you want to delete this album and all its songs? This cannot be undone.",
      )
    ) {
      try {
        await api.delete(`/albums/${albumId}`);
        fetchAlbums(); // Refresh list
      } catch (error) {
        console.error("Failed to delete album:", error);
        alert("Failed to delete album.");
      }
    }
  };

  // --- Song Modal Handlers ---
  const openAddSongModal = (album) => {
    setAlbumForAddingSong(album);
    setSongFormData({ title: "" });
    setIsSongModalOpen(true);
  };

  const handleSongFormChange = (e) => {
    setSongFormData({ title: e.target.value });
  };

  const handleSongSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/albums/${albumForAddingSong.id}/songs`, songFormData);
      setIsSongModalOpen(false);
      fetchAlbums(); // Refresh list
    } catch (error) {
      console.error("Failed to add song:", error);
      alert("Failed to add song.");
    }
  };

  const handleDeleteSong = async (songId) => {
    if (window.confirm("Are you sure you want to delete this song?")) {
      try {
        await api.delete(`/songs/${songId}`);
        fetchAlbums(); // Refresh list
      } catch (error) {
        console.error("Failed to delete song:", error);
        alert("Failed to delete song.");
      }
    }
  };

  if (!user || !user.isAdmin) return <p>Access Denied.</p>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-4xl font-bold">Admin Dashboard</h1>
        <button onClick={openAddAlbumModal} className="btn btn-primary">
          Add New Album
        </button>
      </div>

      {/* Album List */}
      <div className="space-y-6">
        {albums.map((album) => (
          <div key={album.id} className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="card-title text-2xl">{album.title}</h2>
                  <p className="text-base-content/70">{album.artist}</p>
                </div>
                <div className="card-actions">
                  <button
                    onClick={() => openEditAlbumModal(album)}
                    className="btn btn-sm btn-outline btn-info"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteAlbum(album.id)}
                    className="btn btn-sm btn-outline btn-error"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="divider">Songs</div>
              <div className="space-y-2">
                {album.songs.map((song) => (
                  <div
                    key={song.id}
                    className="flex justify-between items-center p-2 rounded-lg bg-base-200"
                  >
                    <span>{song.title}</span>
                    <button
                      onClick={() => handleDeleteSong(song.id)}
                      className="btn btn-xs btn-ghost text-error"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                {album.songs.length === 0 && (
                  <p className="text-center text-sm text-base-content/50">
                    No songs yet.
                  </p>
                )}
              </div>
              <button
                onClick={() => openAddSongModal(album)}
                className="btn btn-secondary btn-sm mt-4 self-start"
              >
                Add Song
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add/Edit Album Modal */}
      {isAlbumModalOpen && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg">
              {editingAlbum ? "Edit Album" : "Add New Album"}
            </h3>
            <form onSubmit={handleAlbumSubmit}>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Title</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={albumFormData.title}
                  onChange={handleAlbumFormChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Artist</span>
                </label>
                <input
                  type="text"
                  name="artist"
                  value={albumFormData.artist}
                  onChange={handleAlbumFormChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Cover Image URL</span>
                </label>
                <input
                  type="text"
                  name="cover_image_url"
                  value={albumFormData.cover_image_url}
                  onChange={handleAlbumFormChange}
                  className="input input-bordered"
                />
              </div>
              <div className="modal-action">
                <button
                  type="button"
                  onClick={() => setIsAlbumModalOpen(false)}
                  className="btn"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Song Modal */}
      {isSongModalOpen && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg">
              Add Song to "{albumForAddingSong?.title}"
            </h3>
            <form onSubmit={handleSongSubmit}>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Song Title</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={songFormData.title}
                  onChange={handleSongFormChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="modal-action">
                <button
                  type="button"
                  onClick={() => setIsSongModalOpen(false)}
                  className="btn"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Add Song
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
