// src/components/TagEditor.jsx

import React, { useState } from 'react';
import { updateTags } from '../api/api.jsx'; // Import updateTags

function TagEditor({ uuid, onClose, tags }) {
    const [editTags, setEditTags] = useState(tags); // Initialize as array
    const [newTag, setNewTag] = useState('');
    const [isAdding, setIsAdding] = useState(false);

    const handleSave = async () => {
        try {
            await updateTags(uuid, editTags); // Call the updateTags API with updated tags
            onClose(); // Close the modal after successful update
        } catch (error) {
            alert('Error updating tags.');
            console.error('Update Tags Error:', error);
        }
    };

    const handleRemoveTag = (tagToRemove) => {
        setEditTags(editTags.filter((tag) => tag !== tagToRemove));
    };

    const handleAddTag = () => {
        if (newTag.trim() !== '' && !editTags.includes(newTag.trim())) {
            setEditTags([...editTags, newTag.trim()]);
            setNewTag('');
            setIsAdding(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddTag();
        }
    };

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20">
            <div className="bg-white p-6 rounded-md w-96 shadow-lg relative">
                <h2 className="text-xl mb-4">Edit Tags</h2>

                {/* Tags Display */}
                <div className="flex flex-wrap gap-2 mb-4">
                    {editTags.map((tag, index) => (
                        <div key={index} className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                            <span>{tag}</span>
                            <button
                                className="ml-2 text-blue-500 hover:text-blue-700 focus:outline-none"
                                onClick={() => handleRemoveTag(tag)}
                                aria-label={`Remove tag ${tag}`}
                            >
                                &times;
                            </button>
                        </div>
                    ))}
                </div>

                {/* Add Tag Section */}
                {isAdding ? (
                    <div className="flex items-center mb-4">
                        <input
                            type="text"
                            value={newTag}
                            onChange={(e) => setNewTag(e.target.value)}
                            onKeyDown={handleKeyDown}
                            className="input input-bordered flex-grow mr-2"
                            placeholder="Enter new tag"
                            autoFocus
                        />
                        <button className="btn btn-secondary btn-sm" onClick={handleAddTag} aria-label="Add tag">
                            +
                        </button>
                        <button
                            className="btn btn-primary btn-sm ml-2"
                            onClick={() => {
                                setIsAdding(false);
                                setNewTag('');
                            }}
                            aria-label="Cancel adding tag"
                        >
                            &times;
                        </button>
                    </div>
                ) : (
                    <button
                        className="btn btn-sm btn-outline flex items-center"
                        onClick={() => setIsAdding(true)}
                        aria-label="Add new tag"
                    >
                        <svg
                            className="w-4 h-4 mr-1"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add Tag
                    </button>
                )}

                {/* Action Buttons */}
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
