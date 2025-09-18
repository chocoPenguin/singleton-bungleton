import axios from '../utils/axiosConfig';

// register
export function registerAuthor(data) {
  return axios.post('/auth/register/', data);
}

// login
export function loginAuthor(data) {
const payload = new URLSearchParams();
  payload.append("grant_type", "password");
  payload.append("username", data.username);
  payload.append("password", data.password);

  return axios.post('/auth/login/', payload, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  });
}