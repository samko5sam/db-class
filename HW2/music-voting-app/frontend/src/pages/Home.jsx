import React, { useState, useEffect, useContext } from 'react';
import api from '../api/axiosConfig';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const Home = () => {
    const [albums, setAlbums] = useState([]);
    const [myVotes, setMyVotes] = useState({ voted_albums: [] });
    const { user } = useContext(AuthContext);

    const fetchAlbums = async () => {
        try {
            const response = await api.get('/albums');
            setAlbums(response.data);
        } catch (error) {
            console.error("Error fetching albums:", error);
        }
    };

    const fetchMyVotes = async () => {
        if (user) {
            try {
                const response = await api.get('/my-votes');
                setMyVotes(response.data);
            } catch (error) {
                console.error("Error fetching my votes:", error);
            }
        }
    };

    useEffect(() => {
        fetchAlbums();
        fetchMyVotes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user]);

    const handleVote = async (albumId) => {
        if (!user) {
            alert("Please log in to vote.");
            return;
        }
        try {
            await api.post(`/vote/album/${albumId}`);
            // Refetch data to update UI
            fetchAlbums();
            fetchMyVotes();
        } catch (error) {
            console.error("Error voting:", error);
        }
    };

    return (
        <div>
            <h1 className="text-4xl font-bold mb-6 text-center">Vote for an Album</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {albums.map(album => (
                    <div key={album.id} className="card bg-base-100 shadow-xl">
                        <figure><img src={album.cover_image_url || 'https://via.placeholder.com/400x400'} alt={album.title} /></figure>
                        <div className="card-body">
                            <h2 className="card-title">{album.title}</h2>
                            <p>{album.artist}</p>
                            <p>Votes: {album.vote_count}</p>
                            <div className="card-actions justify-end">
                                <Link to={`/album/${album.id}`} className="btn btn-secondary">View Songs</Link>
                                <button 
                                    onClick={() => handleVote(album.id)} 
                                    className={`btn ${myVotes.voted_albums.includes(album.id) ? 'btn-success' : 'btn-primary'}`}
                                    disabled={!user}
                                >
                                    {myVotes.voted_albums.includes(album.id) ? 'Voted' : 'Vote'}
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Home;