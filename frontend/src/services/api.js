import axios from 'axios';
import { getToken } from '../utils/storage';

const BASE_URL = 'http://172.17.106.75:5000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const chatAPI = async (message, conversationId = null, context = null) => {
  const res = await api.post('/chat/', { message, conversation_id: conversationId, context });
  return res.data;
};

export const ttsAPI = async (text) => {
  const res = await api.post('/tts/synthesize', { text }, { responseType: 'arraybuffer' });
  return res.data;
};

export const asrAPI = async (audioUri) => {
  const form = new FormData();
  form.append('audio', { uri: audioUri, name: 'audio.wav', type: 'audio/wav' });
  const res = await api.post('/asr/transcribe', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const fileAPI = async (fileUri, fileName, mimeType) => {
  const form = new FormData();
  form.append('file', { uri: fileUri, name: fileName, type: mimeType });
  const res = await api.post('/files/extract', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export default api;
