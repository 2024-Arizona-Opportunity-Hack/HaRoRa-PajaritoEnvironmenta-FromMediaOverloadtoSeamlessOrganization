// src/pages/AuthPage.jsx
import React, { useEffect, useState } from 'react';
import { getProfileInfo, handleLogin } from '../api/api'; // Import the necessary API functions
import DropboxLogo from '../assets/dropbox-1.svg'; // Import Dropbox logo

function AuthPage() {
  const [profile, setProfile] = useState(null);

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

  // If the user is not logged in, show the "Login with Dropbox" button
  if (!profile) {
    return (
      <div className="p-4 flex flex-col justify-center items-center h-screen bg-base-100 text-base-content">
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

  // If the user is logged in, redirect to the Upload page
  return (
    <div className="p-4 flex flex-col justify-center items-center h-screen bg-base-100 text-base-content">
      <h1 className="text-2xl font-bold mb-6">You are already logged in!</h1>
      <p className="text-lg mb-6">
        Redirecting to your dashboard...
      </p>
    </div>
  );
}

export default AuthPage;
