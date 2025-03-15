import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const UploadForm: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setIsUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append('file', acceptedFiles[0]);

    try {
      const response = await axios.post('/api/v1/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setUploadStatus(`Successfully uploaded: ${response.data.filename}`);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('Error uploading document. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed p-6 rounded-lg text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-primary-600">Drop the file here...</p>
        ) : (
          <div>
            <p className="mb-2">Drag & drop a document here, or click to select</p>
            <p className="text-sm text-gray-500">Supported formats: PDF, DOCX, TXT</p>
          </div>
        )}
      </div>

      {isUploading && (
        <div className="mt-4 text-center">
          <p className="text-primary-600">Uploading document...</p>
        </div>
      )}

      {uploadStatus && (
        <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg">
          <p>{uploadStatus}</p>
        </div>
      )}
    </div>
  );
};

export default UploadForm; 