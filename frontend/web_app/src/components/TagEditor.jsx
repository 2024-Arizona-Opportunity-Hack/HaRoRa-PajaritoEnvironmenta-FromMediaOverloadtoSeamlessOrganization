import { useState, useEffect } from 'react';
import { updateTags } from '../api/api.jsx';

function TagEditor({ uuid, onClose, tags: selectedTags }) {
  const [tags, setTags] = useState('');

  useEffect(() => {
    // Update tags state with selectedTags when component mounts or selectedTags changes
    if (selectedTags) {
      setTags(selectedTags.join(', '));
    }
  }, [selectedTags]);

  const handleSave = async () => {
    try {
      await updateTags(uuid, tags.split(',').map((tag) => tag.trim()));
      alert('Tags updated successfully!');
      onClose();
    } catch (error) {
      alert('Error updating tags.');
    }
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-bold text-lg">Edit Tags</h3>
        <input
          type="text"
          className="input input-bordered w-full mt-4"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
        />
        <div className="modal-action">
          <button className="btn" onClick={onClose}>
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
