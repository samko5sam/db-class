import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import Home from './pages/Home.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import AlbumDetail from './pages/AlbumDetail.jsx';

function App() {
  return (
    // Set the data-theme on the root div to let daisyUI know which theme to use initially
    <div className="min-h-screen bg-base-200" data-theme={localStorage.getItem('theme') || 'light'}>
      <Navbar />
      <main className="container mx-auto p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/album/:albumId" element={<AlbumDetail />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;