import React, { useState, useEffect } from 'react';
import Upload from '../components/Upload';
import Reveal from '../components/utils/Reveal.jsx';
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

    return (
        <Reveal>
            <div className="p-4 text-base-content max-w-3xl mx-auto">
                <div className="hero  mb-6 rounded-lg">
                    <div className="hero-content text-center">
                        <div className="max-w-md">
                            <h1 className="text-2xl font-grotesk font-bold">Upload Media</h1>
                            {profile && (
                                <p className="py-6 text-xl">
                                    Welcome, <span className="font-semibold">{profile.name}</span>!
                                </p>
                            )}

                        </div>
                    </div>
                </div>
                {/* Upload Component */}
                <Upload />
            </div>
        </Reveal>

    );
}

export default UploadPage;
