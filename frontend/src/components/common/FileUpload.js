import React, { useState, useRef } from 'react';
import { Upload, X, File, Image as ImageIcon, Check, AlertCircle } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';

const FileUpload = ({ 
  onUploadComplete, 
  folder = "general", 
  accept = "image/*,.pdf,.doc,.docx,.zip",
  multiple = false,
  maxSize = 10 // MB
}) => {
  const toast = useToast();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Vérifier la taille
    const oversizedFiles = selectedFiles.filter(
      file => file.size > maxSize * 1024 * 1024
    );
    
    if (oversizedFiles.length > 0) {
      toast.error(`Certains fichiers dépassent la taille maximale de ${maxSize}MB`);
      return;
    }
    
    setFiles(multiple ? [...files, ...selectedFiles] : selectedFiles);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    
    try {
      if (multiple && files.length > 1) {
        // Upload multiple
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        
        const response = await api.post(`/api/upload/multiple?folder=${folder}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        if (onUploadComplete) {
          onUploadComplete(response.data.uploaded);
        }
        
        setFiles([]);
      } else {
        // Upload single
        const uploadedFiles = [];
        
        for (let i = 0; i < files.length; i++) {
          const formData = new FormData();
          formData.append('file', files[i]);
          
          setUploadProgress(prev => ({ ...prev, [i]: 0 }));
          
          const response = await api.post(`/api/upload?folder=${folder}`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(prev => ({ ...prev, [i]: progress }));
            }
          });
          
          uploadedFiles.push(response.data);
          setUploadProgress(prev => ({ ...prev, [i]: 100 }));
        }
        
        if (onUploadComplete) {
          onUploadComplete(multiple ? uploadedFiles : uploadedFiles[0]);
        }
        
        setFiles([]);
        setUploadProgress({});
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) {
      return <ImageIcon className="w-5 h-5 text-blue-500" />;
    }
    return <File className="w-5 h-5 text-gray-500" />;
  };

  return (
    <div className="space-y-4">
      {/* Zone de drop/sélection */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${uploading ? 'border-gray-300 bg-gray-50 cursor-not-allowed' : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />
        
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600 font-medium">
          Cliquez pour sélectionner {multiple ? 'des fichiers' : 'un fichier'}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Taille max: {maxSize}MB • {accept.split(',').join(', ')}
        </p>
      </div>

      {/* Liste des fichiers sélectionnés */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-700">
              {files.length} fichier{files.length > 1 ? 's' : ''} sélectionné{files.length > 1 ? 's' : ''}
            </h4>
            {!uploading && (
              <button
                onClick={() => setFiles([])}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Tout supprimer
              </button>
            )}
          </div>
          
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
              >
                {getFileIcon(file)}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(file.size)}
                  </p>
                  
                  {/* Barre de progression */}
                  {uploading && uploadProgress[index] !== undefined && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            uploadProgress[index] === 100 ? 'bg-green-500' : 'bg-blue-500'
                          }`}
                          style={{ width: `${uploadProgress[index]}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        {uploadProgress[index]}%
                      </p>
                    </div>
                  )}
                </div>
                
                {uploadProgress[index] === 100 ? (
                  <Check className="w-5 h-5 text-green-500" />
                ) : !uploading ? (
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bouton d'upload */}
      {files.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className={`
            w-full px-4 py-3 rounded-lg font-medium
            transition-colors duration-200
            ${uploading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {uploading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Upload en cours...
            </span>
          ) : (
            `📤 Uploader ${files.length} fichier${files.length > 1 ? 's' : ''}`
          )}
        </button>
      )}
    </div>
  );
};

export default FileUpload;
