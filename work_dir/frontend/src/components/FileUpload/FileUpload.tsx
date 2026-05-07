import { useState, useCallback } from 'react';
import { Upload, X, FileText, FileImage, File, CheckCircle } from 'lucide-react';
import { useToast } from '../Toast';
import { LoadingSpinner } from '../Loading';

export interface UploadFile {
  id: string;
  name: string;
  type: string;
  size: number;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

interface FileUploadProps {
  acceptedTypes?: string[];
  maxSize?: number;
  onFilesUploaded?: (files: File[]) => void;
}

const fileIcons: Record<string, typeof FileText> = {
  pdf: FileText,
  doc: FileText,
  docx: FileText,
  txt: FileText,
  md: FileText,
  jpg: FileImage,
  jpeg: FileImage,
  png: FileImage,
  gif: FileImage,
};

const defaultAcceptedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown', 'image/jpeg', 'image/png', 'image/gif'];
const defaultMaxSize = 50 * 1024 * 1024; // 50MB

export function FileUpload({ acceptedTypes = defaultAcceptedTypes, maxSize = defaultMaxSize, onFilesUploaded }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadFile[]>([]);
  const toast = useToast();

  const getFileExtension = (filename: string) => {
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  const getFileIcon = (filename: string) => {
    const ext = getFileExtension(filename);
    return fileIcons[ext] || File;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const isValidFileType = (file: File) => {
    return acceptedTypes.includes(file.type);
  };

  const isValidFileSize = (file: File) => {
    return file.size <= maxSize;
  };

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    const newFiles: UploadFile[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      if (!isValidFileType(file)) {
        toast.error(`文件 "${file.name}" 类型不支持`);
        continue;
      }

      if (!isValidFileSize(file)) {
        toast.error(`文件 "${file.name}" 超过大小限制 (最大 ${formatFileSize(maxSize)})`);
        continue;
      }

      newFiles.push({
        id: `${Date.now()}-${i}`,
        name: file.name,
        type: file.type,
        size: file.size,
        progress: 0,
        status: 'uploading',
      });
    }

    if (newFiles.length > 0) {
      setUploadingFiles((prev) => [...prev, ...newFiles]);
      simulateUpload(newFiles, files, onFilesUploaded, setUploadingFiles, toast);
    }
  }, [acceptedTypes, maxSize, onFilesUploaded, toast]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleClick = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = acceptedTypes.join(',');
    input.onchange = (e) => handleFiles((e.target as HTMLInputElement).files);
    input.click();
  }, [acceptedTypes, handleFiles]);

  const removeFile = useCallback((id: string) => {
    setUploadingFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  return (
    <div className="w-full">
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <div className={`inline-flex items-center justify-center w-14 h-14 rounded-full mb-4 transition-colors ${
          isDragging ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-400'
        }`}>
          <Upload className="w-7 h-7" />
        </div>
        <h3 className="text-lg font-medium text-gray-700 mb-2">
          {isDragging ? '松开以上传文件' : '拖拽文件到此处或点击上传'}
        </h3>
        <p className="text-sm text-gray-500">
          支持 PDF、Word、TXT、Markdown、图片等格式，单文件最大 {formatFileSize(maxSize)}
        </p>
        
        {isDragging && (
          <div className="absolute inset-0 border-2 border-primary-500 border-solid rounded-xl pointer-events-none" />
        )}
      </div>

      {uploadingFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadingFiles.map((file) => {
            const Icon = getFileIcon(file.name);
            return (
              <div
                key={file.id}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
              >
                <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                  {file.status === 'completed' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : file.status === 'error' ? (
                    <X className="w-5 h-5 text-red-500" />
                  ) : (
                    <Icon className="w-5 h-5 text-gray-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">{file.name}</p>
                  <div className="mt-1">
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          file.status === 'completed'
                            ? 'bg-green-500'
                            : file.status === 'error'
                            ? 'bg-red-500'
                            : 'bg-primary-500'
                        }`}
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        {file.status === 'completed'
                          ? '上传完成'
                          : file.status === 'error'
                          ? file.error || '上传失败'
                          : `${file.progress}%`}
                      </span>
                      <span className="text-xs text-gray-400">{formatFileSize(file.size)}</span>
                    </div>
                  </div>
                </div>
                {file.status !== 'uploading' && (
                  <button
                    onClick={() => removeFile(file.id)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
                {file.status === 'uploading' && (
                  <LoadingSpinner size="sm" className="text-primary-500" />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function simulateUpload(
  uploadFiles: UploadFile[],
  originalFiles: FileList,
  onFilesUploaded?: (files: File[]) => void,
  setUploadingFiles?: React.Dispatch<React.SetStateAction<UploadFile[]>>,
  toast?: ReturnType<typeof useToast>
) {
  const filesArray = Array.from(originalFiles);
  
  uploadFiles.forEach((uploadFile, index) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        if (setUploadingFiles) {
          setUploadingFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFile.id ? { ...f, progress: 100, status: 'completed' as const } : f
            )
          );
        }
        
        if (index === uploadFiles.length - 1) {
          if (onFilesUploaded) {
            onFilesUploaded(filesArray);
          }
          if (toast) {
            toast.success(`成功上传 ${uploadFiles.length} 个文件`);
          }
        }
      } else {
        if (setUploadingFiles) {
          setUploadingFiles((prev) =>
            prev.map((f) => (f.id === uploadFile.id ? { ...f, progress } : f))
          );
        }
      }
    }, 200);
  });
}
