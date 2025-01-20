import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { getProfileInfo, handleLogin } from '../api/api'; // Import the necessary API functions
import DropboxLogo from '../assets/dropbox-1.svg'; // Import Dropbox logo

function AuthPage() {
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate(); // Initialize the navigate hook

  // Fetch the user's profile info on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      const { response, err } = await getProfileInfo();
      if (err) {
        setProfile(null); // Ensure profile is null in case of error
      } else {
        setProfile(response); // Set profile data if successful
      }
    };

    fetchProfile();
  }, []);

  // If the user is logged in, redirect to the Upload page
  useEffect(() => {
    if (profile) {
      navigate('/upload'); // Redirect to /upload if logged in
    }
  }, [profile, navigate]);

  // If the user is not logged in, show the "Login with Dropbox" button
  if (!profile) {
    return (
      <div className="mt-1 p-3 flex flex-col justify-center items-center h-screen bg-base-100 text-base-content">
        <h1 className="text-4xl font-bold mb-6">Welcome to Media Manager</h1>
        <p className="text-lg mb-6">
          Please log in to access the application.
        </p>
        <button
          className="btn btn-primary py-3 px-6 flex items-center"
          onClick={handleLogin}
        >
          <img src={DropboxLogo} alt="Dropbox Logo" className="w-6 h-6 mr-2" />
          Login with Dropbox
        </button>
      </div>
    );
  }

  return null; // Return null since the user is redirected if logged in
}

export default AuthPage;
