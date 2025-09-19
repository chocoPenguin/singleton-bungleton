import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Get axios instance with auth headers
const getApiInstance = () => {
  const token = localStorage.getItem('token');
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json'
    }
  });
};

// Get all resources
export const getAllResources = async () => {
  const api = getApiInstance();
  return api.get('/resources/');
};

// Get resources by author
export const getResourcesByAuthor = async (authorId) => {
  const api = getApiInstance();
  return api.get(`/resources/author/${authorId}`);
};

// Get single resource
export const getResource = async (resourceId) => {
  const api = getApiInstance();
  return api.get(`/resources/${resourceId}`);
};

// Create new resource
export const createResource = async (resourceData) => {
  const api = getApiInstance();
  return api.post('/resources/', resourceData);
};

// Update resource
export const updateResource = async (resourceId, resourceData) => {
  const api = getApiInstance();
  return api.put(`/resources/${resourceId}`, resourceData);
};

// Delete resource
export const deleteResource = async (resourceId) => {
  const api = getApiInstance();
  return api.delete(`/resources/${resourceId}`);
};

// Upload file resource (legacy support)
export const uploadFileResource = async (formData) => {
  const api = getApiInstance();
  api.defaults.headers['Content-Type'] = 'multipart/form-data';
  return api.post('/resources/file', formData);
};

// Create text resource (legacy support)
export const createTextResource = async (resourceData) => {
  const api = getApiInstance();
  return api.post('/resources/text', resourceData);
};

// Get resource type labels
export const getResourceTypeLabel = (type) => {
  const types = {
    'SP': 'SharePoint',
    'LS': 'Local Storage',
    'GC': 'Google Cloud',
    'S3': 'AWS S3'
  };
  return types[type] || type;
};

// Get resource type options for dropdown
export const getResourceTypeOptions = () => {
  return [
    { label: 'SharePoint', value: 'SP' },
    { label: 'Local Storage', value: 'LS' },
    { label: 'Google Cloud', value: 'GC' },
    { label: 'AWS S3', value: 'S3' }
  ];
};