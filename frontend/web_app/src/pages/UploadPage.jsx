// src/pages/UploadPage.jsx
import React, { useState, useEffect } from 'react';
import Upload from '../components/Upload';
import { getProfileInfo, handleLogout } from '../api/api'; // Import the necessary API functions

function UploadPage() {
  const [profile, setProfile] = useState(null);

  // Fetch the user's profile info on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      const { response } = await getProfileInfo();
      setProfile(response);
    };

    fetchProfile();
  }, []);

  // Handle logout
  const handleLogoutClick = async () => {
    await handleLogout(setProfile); // Log out the user
    window.location.reload(); // Refresh the page to reset the authentication state
  };

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
