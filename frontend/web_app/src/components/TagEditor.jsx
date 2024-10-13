import { useState, useEffect } from 'react';
import { getTags, updateTags } from '../api/backup';

function TagEditor({ uuid, onClose }) {
  const [tags, setTags] = useState('');

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const data = await getTags(uuid);
        setTags(data.tags.join(', '));
      } catch (error) {
        console.error('Error fetching tags:', error);
      }
    };

    fetchTags();
  }, [uuid]);

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
