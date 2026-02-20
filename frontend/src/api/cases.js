import api from './client'

export const getCases = async () => {
  const { data } = await api.get('/cases')
  return data
}

export const getCaseById = async (id) => {
  const { data } = await api.get(`/cases/${id}`)
  return data
}

export const createCase = async (caseData) => {
  const { data } = await api.post('/cases', caseData)
  return data
}

export const deleteCase = async (id) => {
  await api.delete(`/cases/${id}`)
}

export const uploadFile = async (caseId, file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const { data } = await api.post(`/cases/${caseId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      onProgress?.(percentCompleted)
    }
  })
  return data
}

export const getProcessingStatus = async (caseId) => {
  const { data } = await api.get(`/cases/${caseId}/processing-status`)
  return data
}

export const getTimeline = async (caseId, filters) => {
  const { data } = await api.get(`/cases/${caseId}/timeline`, { params: filters })
  return data
}

export const getRuleResults = async (caseId) => {
  const { data } = await api.get(`/cases/${caseId}/rules`)
  return data
}

export const runAnomalyDetection = async (caseId) => {
  const { data } = await api.post(`/cases/${caseId}/anomaly/run`)
  return data
}

export const getAnomalyResults = async (caseId) => {
  const { data } = await api.get(`/cases/${caseId}/anomaly`)
  return data
}

export const getGraphData = async (caseId, filters) => {
  const { data } = await api.get(`/cases/${caseId}/graph`, { params: filters })
  return data
}

export const getRiskScore = async (caseId) => {
  const { data } = await api.get(`/cases/${caseId}/risk`)
  return data
}

export const generateReport = async (caseId, title = 'Investigation Report') => {
  const { data } = await api.post(`/cases/${caseId}/report/generate`, { title })
  return data
}

export const getReports = async (caseId) => {
  const { data } = await api.get(`/cases/${caseId}/reports`)
  return { reports: data, summary: null }
}
