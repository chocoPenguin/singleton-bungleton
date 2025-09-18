import axios from '../utils/axiosConfig';

// Get users by group ID
export function getUsersByGroup(groupId) {
  return axios.get(`/users/group/${groupId}`);
}

// Get user by ID
export function getUserById(userId) {
  return axios.get(`/users/${userId}`);
}

// Get current user info
export function getCurrentUser() {
  return axios.get('/users/me');
}

// Create new user
export function createUser(data) {
  return axios.post('/users/', data);
}

// Update user
export function updateUser(userId, data) {
  return axios.put(`/users/${userId}`, data);
}

// Delete user
export function deleteUser(userId) {
  return axios.delete(`/users/${userId}`);
}

// Add user to group
export function addUserToGroup(groupId, userId) {
  return axios.post(`/users/group/${groupId}/${userId}`);
}

// Remove user from group
export function removeUserFromGroup(groupId, userId) {
  return axios.delete(`/users/group/${groupId}/${userId}`);
}