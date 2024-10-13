// src/components/Upload.jsx
import { useState } from 'react';
import { uploadFiles } from '../api/api';
import { useDropzone } from 'react-dropzone';

function Upload() {
  const [files, setFiles] = useState([]);
  const [tags, setTags] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const onDrop = (acceptedFiles) => {
    setFiles(acceptedFiles);
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
    multiple: true,
    accept: 'image/*,video/*',
  });

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
      {/* Drag and Drop Area */}
      <div
        {...getRootProps()}
        className={`border-4 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
      >
        <input {...getInputProps()} />
        <svg
          className="w-16 h-16 text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 48 48"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M44 32V16a4 4 0 00-4-4H8a4 4 0 00-4 4v16"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="4"
          />
          <path
            d="M4 32l20 12 20-12"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="4"
          />
        </svg>
        <p className="text-lg text-gray-600 text-center">
          Drag and drop files here, or click to select files
        </p>
        {files.length > 0 && (
          <ul className="mt-4 list-disc text-gray-600">
            {files.map((file) => (
              <li key={file.path}>{file.name}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Tags Input 
    
      <div className="mt-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Tags
        </label>
        <input
          type="text"
          placeholder="Enter tags separated by commas"
          className="input input-bordered w-full"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
        />
      </div>*/}

      {/* Upload Button */}
      <button className="btn btn-primary mt-6 w-full" onClick={handleUpload}>
        Upload
      </button>
    </div>
  );
}

export default Upload;
