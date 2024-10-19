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


  return (
    <div className="p-4  text-base-content max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold my-4">Upload Media</h1>
      {profile && (
        <div className="mb-6">
          <h2 className="text-xl font-bold">Welcome, {profile.name}!</h2>
          <p>Email: {profile.email}</p>
        </div>
      )}
      {/* Upload Component */}
      <Upload />


    </div>
  );
}

export default UploadPage;
