import React, { useState, useRef } from 'react';
import { X, Trash2, Upload } from 'lucide-react';
import { uploadFiles } from '@/api.js';

export default function FileUploadModal({ isOpen, onClose }) {
  const [files, setFiles] = useState([]);
  const [tags, setTags] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  
  const handleFileSelect = (selectedFiles) => {
    const newFiles = Array.from(selectedFiles).filter(file => {
      const type = file.type.toLowerCase();
      return type === 'image/jpeg' || type === 'image/jpg' || type === 'image/png';
    });
    
    setFiles(prev => [...prev, ...newFiles]);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileSelect(droppedFiles);
  };

  const removeFile = (indexToRemove) => {
    setFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const removeAllFiles = () => {
    setFiles([]);
  };

  const handleUpload = () => {
    // Here you would typically send the files and tags to your server
    uploadFiles(files, tags, undefined)
    console.log('Files to upload:', files);
    console.log('Tags:', tags);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box max-w-3xl">
        <button 
          className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
          onClick={onClose}
        >
          ✕
        </button>
        
        <h3 className="font-bold text-lg mb-6">Upload Files</h3>

        <div className="space-y-6">
          {/* Tags Input */}
          <div className="form-control w-full">
            <label className="label">
              <span className="label-text">Tags</span>
            </label>
            <input
              type="text"
              placeholder="Add multiple tags, separated by commas"
              className="input input-bordered w-full"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
          </div>

          {/* Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
              ${isDragging ? 'border-primary bg-base-200' : 'border-base-300'}`}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              multiple
              accept=".jpg,.jpeg,.png"
              onChange={(e) => handleFileSelect(e.target.files)}
            />
            <div className="flex flex-col items-center space-y-2">
              <Upload className="w-12 h-12 text-base-content opacity-50" />
              <p className="text-sm text-base-content opacity-70">
                Drag and drop images here, or click to select files
              </p>
              <p className="text-xs text-base-content opacity-50">
                Supported formats: JPG, JPEG, PNG
              </p>
            </div>
          </div>

          {/* Selected Files */}
          {files.length > 0 && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-sm opacity-70">
                  {files.length} file(s) selected
                </p>
                <button
                  className="btn btn-sm btn-outline hover:text-base-100 btn-error gap-2"
                  onClick={removeAllFiles}
                >
                  <Trash2 className="w-4 h-4" />
                  Remove All
                </button>
              </div>

              <div className="overflow-x-auto">
                <div className="flex space-x-4 p-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="relative flex-shrink-0 w-24 h-24 group rounded-lg overflow-hidden"
                    >
                      <img
                        src={URL.createObjectURL(file)}
                        alt={`Preview ${index}`}
                        className="w-full h-full object-cover"
                      />
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(index);
                        }}
                        className="absolute bottom-0 right-0 bg-black bg-opacity-50 p-1 rounded-tl-lg hover:bg-opacity-70 transition-colors"
                      >
                        <Trash2 className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="modal-action">
            <button className="btn" onClick={onClose}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleUpload}>
              Upload
            </button>
          </div>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose}>
        <button className="cursor-default">close</button>
      </div>
    </div>
  );
}
