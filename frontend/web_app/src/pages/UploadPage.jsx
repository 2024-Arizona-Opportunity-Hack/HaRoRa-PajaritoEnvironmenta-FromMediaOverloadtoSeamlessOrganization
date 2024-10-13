// src/pages/UploadPage.jsx
import React, { useEffect, useState } from 'react';
import Upload from '../components/Upload';
import { getProfileInfo, handleLogin, handleLogout } from '../api/api'; // Import the necessary API functions
import DropboxLogo from '../assets/dropbox-1.svg'; // Import Dropbox logo

function UploadPage() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  // Fetch the user's profile info on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      const { response, err } = await getProfileInfo();
      if (err) {
        setError(err);  // If error occurs (like not logged in), set the error message
        setProfile(null); // Ensure profile is null in case of error
      } else {
        setProfile(response); // Set profile data if successful
        setError(null); // Clear error if logged in
      }
    };

    fetchProfile();
  }, []);

  // Handle logout
  const handleLogoutClick = async () => {
    await handleLogout(); // Log out the user
    setProfile(null); // Clear profile info after logout
    setError('You have been logged out.');
  };

  // If the user is not logged in, show the "Login with Dropbox" button
  if (!profile) {
    return (
      <div className="p-4 flex flex-col justify-center items-center h-screen bg-base-100 text-base-content">
        <h1 className="text-4xl font-bold mb-6">Welcome to Media Manager</h1>
        <p className="text-lg mb-6">
          Please log in to upload your media and manage your files.
        </p>
        <button
          className="btn btn-primary py-3 px-6"
          onClick={handleLogin}
        >
          <img src={DropboxLogo} alt="Dropbox Logo" className="w-6 h-6 mr-2" /> 
          Login with Dropbox
        </button>
      </div>
    );
  }

  // If the user is logged in, show profile info, upload form, and logout button
  return (
    <div className="p-4 bg-base-100 text-base-content">
      <h1 className="text-2xl font-bold my-4">Upload Media</h1>
      {profile && (
        <div className="mb-6">
          <h2 className="text-xl font-bold">Welcome, {profile.name}!</h2>
          <p>Email: {profile.email}</p>
        </div>
      )}
      
      {/* Upload Component */}
      <Upload /> 

      {/* Logout Button */}
      <button
        className="btn btn-error mt-4"
        onClick={handleLogoutClick}
      >
        Logout
      </button>
    </div>
  );
}

export default UploadPage;
