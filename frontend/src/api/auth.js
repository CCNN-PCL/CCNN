import axios from 'axios';

const API_URL = process.env.CYBERTWIN;

export default {
  register(userData) {
    // return axios.post(`${API_URL}/api/register`, userData);
    return axios.post('/api/register', userData);

  },
  login(userdata) {
    // return axios.post(`${API_URL}/api/login`, userdata);
    return axios.post('/api/login', userdata);

  }
};
