import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import Card from '../components/Card'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import { uploadFile, getProcessingStatus } from '../api/cases'

const UploadPage = () => {
  const { id } = useParams()
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [status, setStatus] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  useEffect(() => {
    let interval
    if (processing) {
      interval = setInterval(async () => {
        try {
          const data = await getProcessingStatus(id)
          setStatus(data)
          if (data.status === 'completed' || data.status === 'failed') {
            setProcessing(false)
          }
        } catch (error) {
          console.error('Failed to fetch status:', error)
        }
      }, 2000)
    }
    return () => clearInterval(interval)
  }, [processing, id])

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      setSelectedFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploading(true)
    try {
      await uploadFile(id, selectedFile, setUploadProgress)
      setProcessing(true)
      setUploading(false)
    } catch (error) {
      console.error('Upload failed:', error)
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">File Upload</h1>

      <Card>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
            dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-gray-700'
          }`}
        >
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-500" />
          <p className="text-lg mb-2">Drag and drop your file here</p>
          <p className="text-sm text-gray-500 mb-4">or</p>
          <label className="btn-primary cursor-pointer inline-block">
            Browse Files
            <input type="file" onChange={handleFileChange} className="hidden" />
          </label>
        </div>

        {selectedFile && (
          <div className="mt-6 p-4 bg-dark-bg rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-blue-500" />
              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <button onClick={handleUpload} disabled={uploading} className="btn-primary">
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        )}

        {uploading && (
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span>Uploading...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
            </div>
          </div>
        )}
      </Card>

      {processing && (
        <Card>
          <div className="flex items-center gap-3 mb-4">
            <Loader size="sm" />
            <h2 className="text-lg font-semibold">Processing Data</h2>
          </div>
          {status && (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Records Processed</span>
                <span className="font-medium">{status.records_processed || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Messages</span>
                <span className="font-medium">{status.message_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Calls</span>
                <span className="font-medium">{status.call_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Status</span>
                <Badge variant={status.status === 'completed' ? 'success' : 'info'}>{status.status}</Badge>
              </div>
            </div>
          )}
        </Card>
      )}

      {status?.errors?.length > 0 && (
        <Card>
          <div className="flex items-center gap-3 mb-4 text-red-400">
            <AlertCircle className="w-5 h-5" />
            <h2 className="text-lg font-semibold">Processing Errors</h2>
          </div>
          <div className="space-y-2">
            {status.errors.map((error, idx) => (
              <div key={idx} className="text-sm text-gray-400 p-2 bg-red-900/20 rounded">
                {error}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}

export default UploadPage
