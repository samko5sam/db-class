import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axiosConfig';
import { AuthContext } from '../context/AuthContext.jsx';

const AlbumDetail = () => {
    const { albumId } = useParams();
    const [songs, setSongs] = useState([]);
    const [myVotes, setMyVotes] = useState({ voted_songs: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user } = useContext(AuthContext);

    const fetchData = async () => {
        try {
            setError('');
            setLoading(true);
            const songsResponse = await api.get(`/albums/${albumId}/songs`);
            setSongs(songsResponse.data);

            if (user) {
                const votesResponse = await api.get('/my-votes');
                setMyVotes(votesResponse.data);
            }
        } catch (err) {
            console.error("Error fetching album details:", err);
            setError("Could not load album data. It might not exist.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [albumId, user]); // Refetch if the album ID or user changes

    const handleVote = async (songId) => {
        if (!user) {
            alert("Please log in to vote.");
            return;
        }
        try {
            await api.post(`/vote/song/${songId}`);
            // Refetch data to instantly update vote counts and button state
            fetchData();
        } catch (error) {
            console.error("Error voting for song:", error);
            alert("Your vote could not be cast. Please try again.");
        }
    };

    if (loading) {
        return <div className="text-center"><span className="loading loading-spinner loading-lg"></span></div>;
    }
    
    if (error) {
        return <div className="alert alert-error">{error}</div>;
    }

    return (
        <div>
            <div className="mb-8">
                <Link to="/" className="btn btn-outline">&larr; Back to Albums</Link>
                <h1 className="text-4xl font-bold mt-4">Songs for Voting</h1>
                <p className="text-lg text-base-content/70">Click to vote for your favorite song on this album.</p>
            </div>
            
            <div className="space-y-4">
                {songs.length > 0 ? (
                    songs.map(song => (
                        <div key={song.id} className="card bg-base-100 shadow-md">
                            <div className="card-body flex-row items-center justify-between">
                                <div>
                                    <h2 className="card-title text-2xl">{song.title}</h2>
                                    <p className="text-base-content/60">Current Votes: {song.vote_count}</p>
                                </div>
                                <div className="card-actions">
                                    <button
                                        onClick={() => handleVote(song.id)}
                                        className={`btn w-28 ${myVotes.voted_songs.includes(song.id) ? 'btn-success' : 'btn-primary'}`}
                                        disabled={!user}
                                    >
                                        {myVotes.voted_songs.includes(song.id) ? 'Voted ✓' : 'Vote'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <p>No songs have been added to this album yet.</p>
                )}
            </div>
        </div>
    );
};

export default AlbumDetail;