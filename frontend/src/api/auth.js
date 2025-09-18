import axios from '../utils/axiosConfig';

// register
export function registerAuthor(data) {
  const params = new URLSearchParams({
    email: data.email,
    password: data.password,
    name: data.name
  });

  return axios.post(`/auth/register?${params.toString()}`);
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

// Get all authors
export function getAllAuthors() {
  return axios.get('/authors/');
}