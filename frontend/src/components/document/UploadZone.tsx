import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useTranslation } from 'react-i18next'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { uploadDocument, setUploadProgress } from '@/features/documents/documentsSlice'
import { Upload } from 'lucide-react'

const UploadZone = () => {
  const { t } = useTranslation('documents')
  const dispatch = useAppDispatch()
  const { uploadProgress, isLoading } = useAppSelector((state) => state.documents)

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach((file) => {
        dispatch(
          uploadDocument({
          file,
          onProgress: (progress) => dispatch(setUploadProgress(progress)),
        })
        )
      })
    },
    [dispatch]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/html': ['.html'],
    },
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
        isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
      }`}
    >
      <input {...getInputProps()} />
      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      {isLoading ? (
        <div>
          <p className="text-lg text-gray-600 mb-2">
          {uploadProgress < 100 ? t('upload.uploading') : t('upload.processing')}
        </p>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
        </div>
      ) : (
        <div>
          <p className="text-lg text-gray-600 mb-2">
          {isDragActive ? '释放文件开始上传' : t('upload.dropzone')}
        </p>
        <p className="text-sm text-gray-500">{t('upload.supportedFormats')}</p>
        </div>
      )}
    </div>
  )
}

export default UploadZone
