// src/pages/UploadPage.jsx
import React, { useEffect, useState } from 'react';
import Upload from '../components/Upload';
import { getProfileInfo, handleLogin, handleLogout } from '../api/api'; // Import the necessary API functions

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
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-2xl font-bold my-4">Upload Media</h1>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          onClick={handleLogin}
        >
          Login with Dropbox
        </button>
      </div>
    );
  }

  // If the user is logged in, show profile info, upload form, and logout button
  return (
    <div className="container mx-auto max-w-4xl">
      <h1 className="text-2xl font-bold my-4">Upload Media</h1>
      {profile && (
        <div className="mb-6">
          <h2 className="text-xl font-bold">Welcome, {profile.name}!</h2>
          <p>Email: {profile.email}</p>
        </div>
      )}
      <Upload /> {/* The Upload component */}
      <button
        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mt-4"
        onClick={handleLogoutClick}
      >
        Logout
      </button>
    </div>
  );
}

export default UploadPage;
