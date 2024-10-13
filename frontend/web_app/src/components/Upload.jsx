

// components/Upload.jsx
import { useState } from 'react';
import { uploadFiles } from '../api/api';

function Upload() {
  const [files, setFiles] = useState([]);
  const [tags, setTags] = useState('');

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
  };

  const handleUpload = async () => {
    try {
      await uploadFiles(files, tags);
      alert('Files uploaded successfully!');
      setFiles([]);
      setTags('');
    } catch (error) {
      alert('Error uploading files.');
    }
  };

  return (
    <div className="p-4">
      <div className="border-dashed border-4 border-gray-200 p-4">
        <input type="file" multiple onChange={handleFileChange} />
        <p>Drag and drop files here or click to select files</p>
      </div>
      <div className="mt-4">
        <input
          type="text"
          placeholder="Enter tags"
          className="input input-bordered w-full"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
        />
      </div>
      <button className="btn btn-primary mt-4" onClick={handleUpload}>
        Upload
      </button>
    </div>
  );
}

export default Upload;
