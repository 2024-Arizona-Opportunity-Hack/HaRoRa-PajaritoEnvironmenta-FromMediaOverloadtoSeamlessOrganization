// src/components/Upload.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

function Upload() {
  const [files, setFiles] = useState([]);
  const [tags, setTags] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrls, setPreviewUrls] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = (acceptedFiles) => {
    setFiles(acceptedFiles);

    // Generate preview URLs
    const previews = acceptedFiles.map((file) =>
      Object.assign(file, {
        preview: URL.createObjectURL(file),
      })
    );
    setPreviewUrls(previews);
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
    multiple: true,
    accept: 'image/*,video/*',
  });

  const handleUpload = async () => {
    setIsUploading(true);
    setUploadProgress(0);
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      formData.append('tags', tags);

      await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      alert('Files uploaded successfully!');
      setFiles([]);
      setTags('');
      setPreviewUrls([]);
      setUploadProgress(0);
    } catch (error) {
      alert('Error uploading files.');
    } finally {
      setIsUploading(false);
    }
  };

  useEffect(() => {
    // Clean up the object URLs when component unmounts
    return () => {
      previewUrls.forEach((file) => URL.revokeObjectURL(file.preview));
    };
  }, [previewUrls]);

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
        {previewUrls.length > 0 ? (
          <>
            <div className="grid grid-cols-4 gap-4 w-full">
              {previewUrls.map((file) => (
                <div key={file.name} className="relative">
                  <img
                    src={file.preview}
                    alt={file.name}
                    className="w-full h-24 object-cover rounded"
                  />
                  {isUploading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
                      <span className="loading loading-spinner loading-md"></span>
                    </div>
                  )}
                </div>
              ))}
            </div>
            {isUploading && (
              <div className="w-full mt-4">
                <progress
                  className="progress progress-primary w-full"
                  value={uploadProgress}
                  max="100"
                ></progress>
                <p className="text-center text-gray-600">{uploadProgress}%</p>
              </div>
            )}
          </>
        ) : (
          <>
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
          </>
        )}
      </div>

      {/* Tags Input */}
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
      </div>

      {/* Upload Button */}
      <button
        className="btn btn-primary mt-6 w-full"
        onClick={handleUpload}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}

export default Upload;
