import axios from '../utils/axiosConfig';

// Get groups by author ID
export function getGroupsByAuthor(authorId) {
  return axios.get(`/groups/author/${authorId}`);
}

// Get all groups
export function getAllGroups() {
  return axios.get('/groups/');
}

// Get group by ID
export function getGroupById(groupId) {
  return axios.get(`/groups/${groupId}`);
}

// Create new group
export function createGroup(data) {
  return axios.post('/groups/', data);
}

// Update group
export function updateGroup(groupId, data) {
  return axios.put(`/groups/${groupId}`, data);
}

// Delete group
export function deleteGroup(groupId) {
  return axios.delete(`/groups/${groupId}`);
}