import axios from '../utils/axiosConfig';

// Create new question set
export function createQuestionSet(data) {
  return axios.post('/question_sets/', data);
}

// Get question sets by author
export function getQuestionSetsByAuthor(authorId) {
  return axios.get(`/question_sets/author/${authorId}`);
}

// Get question set by ID
export function getQuestionSetById(id) {
  return axios.get(`/question_sets/${id}`);
}

// Update question set
export function updateQuestionSet(id, data) {
  return axios.put(`/question_sets/${id}`, data);
}

// Delete question set
export function deleteQuestionSet(id) {
  return axios.delete(`/question_sets/${id}`);
}

// Get question generation status
export function getQuestionGenerationStatus(questionSetId) {
  return axios.get(`/question_sets/${questionSetId}/status`);
}

// Start question generation (async)
export function startQuestionGeneration(questionSetId) {
  return axios.post(`/question_sets/${questionSetId}/generate`);
}

// Generate quiz with AI (Microsoft AI Foundry Agent)
export function generateQuizWithAI(data) {
  return axios.post('/question_sets/generate', data);
}

// Get all question sets (for history view)
export function getAllQuestionSets() {
  return axios.get('/question_sets/');
}

// Get question set details with questions and assignments
export function getQuestionSetDetails(questionSetId) {
  return axios.get(`/question_sets/${questionSetId}/details`);
}