import { useState, useCallback } from 'react';
import { chatAPI, ttsAPI, asrAPI, fileAPI } from '../services/api';
import { playAudioFromBytes } from '../utils/audio';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fileContext, setFileContext] = useState(null);

  const addMessage = (role, content) => {
    const msg = { id: Date.now().toString(), role, content, timestamp: new Date() };
    setMessages(prev => [...prev, msg]);
    return msg;
  };

  const sendMessage = useCallback(async (text) => {
    addMessage('user', text);
    setLoading(true);
    try {
      const res = await chatAPI(text, null, fileContext);
      addMessage('assistant', res.response);
      setLoading(false); // stop indicator as soon as response arrives
      // TTS runs in background — does not block UI
      ttsAPI(res.response).then(playAudioFromBytes).catch(() => {});
    } catch (e) {
      addMessage('assistant', 'Pane dambudziko rekubatana. Ndapota edza zvakare.');
      setLoading(false);
    }
  }, [fileContext]);

  const sendVoice = useCallback(async (audioUri) => {
    setLoading(true);
    try {
      const { transcript } = await asrAPI(audioUri);
      await sendMessage(transcript);
    } catch (e) {
      addMessage('assistant', 'Handikwanisi kunzwa. Ndapota edza zvakare.');
      setLoading(false);
    }
  }, [sendMessage]);

  const uploadFile = useCallback(async (uri, name, type) => {
    setLoading(true);
    try {
      const { text } = await fileAPI(uri, name, type);
      setFileContext(text);
      addMessage('assistant', 'Faira rakagamuchirwa. Inguva yako kubvunza mibvunzo nezvairi.');
    } catch (e) {
      addMessage('assistant', 'Handikwanisi kuvhura faira. Ndapota edza zvakare.');
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, sendMessage, sendVoice, uploadFile };
};
