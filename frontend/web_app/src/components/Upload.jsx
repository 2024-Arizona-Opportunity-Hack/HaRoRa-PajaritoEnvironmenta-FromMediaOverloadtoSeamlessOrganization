// src/components/Upload.jsx
import { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadFiles } from '../api/api'; // Import the upload function from api.jsx

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
        accept: 'image/*',
    });

    const handleUpload = async () => {
        if (files.length === 0) {
            alert('Please select files to upload.');
            return;
        }

        setIsUploading(true);
        setUploadProgress(0);

        try {
            // Pass a callback to track upload progress
            await uploadFiles(files, tags, (progressEvent) => {
                const { loaded, total } = progressEvent;
                const percentCompleted = Math.round((loaded * 100) / total);
                setUploadProgress(percentCompleted);
            });
            setUploadProgress(100);

            // alert('Files uploaded successfully!');
            setFiles([]);
            setTags('');
            setPreviewUrls([]);
            // setUploadProgress(0);
        } catch (error) {
            console.error('Upload error:', error);
            alert('Error uploading files.');
        } finally {
            setIsUploading(false);
        }
    };

    useEffect(() => {
        // Clean up the object URLs when component unmounts or files change
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
                            <path d="M4 32l20 12 20-12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
                        </svg>
                        <p className="text-lg text-gray-600 text-center">
                            Drag and drop files here, or click to select files
                        </p>
                    </>
                )}
            </div>

            {/* Tags Input */}
            <div className="mt-6">
                <label className="block text-primary text-sm font-bold mb-2">Tags</label>
                <input
                    type="text"
                    placeholder="Enter tags separated by commas"
                    className="input input-bordered w-full"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    disabled={isUploading} // Disable input during upload
                />
            </div>

            {/* Upload Button */}
            <button
                className="btn btn-primary mt-6 w-full"
                onClick={handleUpload}
                disabled={isUploading || files.length === 0}
            >
                {isUploading ? `Uploading... ${uploadProgress}%` : 'Upload'}
            </button>
        </div>
    );
}

export default Upload;
