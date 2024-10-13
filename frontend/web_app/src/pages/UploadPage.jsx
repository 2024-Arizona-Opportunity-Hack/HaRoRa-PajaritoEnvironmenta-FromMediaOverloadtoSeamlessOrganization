// src/pages/UploadPage.jsx
import React from 'react';
import Upload from '../components/Upload';

function UploadPage() {
  return (
    <div className="container mx-auto max-w-4xl">
      <h1 className="text-2xl font-bold my-4">Upload Media</h1>
      <Upload />
    </div>
  );
}

export default UploadPage;
