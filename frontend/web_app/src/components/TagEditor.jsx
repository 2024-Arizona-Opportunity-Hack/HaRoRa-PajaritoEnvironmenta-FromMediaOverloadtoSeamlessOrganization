// src/components/TagEditor.jsx

import React, { useState } from 'react';
import { updateTags } from '../api/api.jsx'; // Import updateTags

function TagEditor({ uuid, onClose, tags }) {
    const [editTags, setEditTags] = useState(tags.join(', '));

    const handleSave = async () => {
        const updatedTags = editTags.split(',').map((tag) => tag.trim());
        try {
            await updateTags(uuid, updatedTags); // Call the updateTags API
            onClose(); // Close the modal after successful update
        } catch (error) {
            alert('Error updating tags.');
            console.error('Update Tags Error:', error);
        }
    };

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white p-6 rounded-md w-96">
                <h2 className="text-xl mb-4">Edit Tags</h2>
                <input
                    type="text"
                    value={editTags}
                    onChange={(e) => setEditTags(e.target.value)}
                    className="input input-bordered w-full mb-4"
                    placeholder="Enter tags separated by commas"
                />
                <div className="flex justify-end space-x-2">
                    <button className="btn btn-secondary" onClick={onClose}>
                        Cancel
                    </button>
                    <button className="btn btn-primary" onClick={handleSave}>
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
}

export default TagEditor;
