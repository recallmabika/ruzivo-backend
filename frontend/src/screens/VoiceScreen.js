import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useChat } from '../hooks/useChat';
import { startRecording, stopRecording } from '../utils/audio';
import MessageBubble from '../components/MessageBubble';
import { FlatList } from 'react-native';

const VoiceScreen = () => {
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const { messages, loading, sendVoice } = useChat();

  const handleMicPress = async () => {
    if (isRecording) {
      setIsRecording(false);
      const uri = await stopRecording(recording);
      setRecording(null);
      await sendVoice(uri);
    } else {
      try {
        const rec = await startRecording();
        setRecording(rec);
        setIsRecording(true);
      } catch (e) {
        Alert.alert('Kukanganisa', 'Handikwanisi kushandisa maiki. Tenderera Ruzivo kushandisa maiki.');
      }
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Nhaurirano yeInzwi</Text>
        <Text style={styles.headerSubtitle}>Taura muShona</Text>
      </View>

      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <MessageBubble message={item} />}
        style={styles.messageList}
      />

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator color="#2E7D32" />
          <Text style={styles.loadingText}>Ruzivo iri kupindura...</Text>
        </View>
      )}

      <View style={styles.micContainer}>
        <TouchableOpacity
          style={[styles.micButton, isRecording && styles.micButtonActive]}
          onPress={handleMicPress}
          disabled={loading}
        >
          <Ionicons name={isRecording ? 'stop' : 'mic'} size={40} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.micLabel}>
          {isRecording ? 'Kwata kuzomisa...' : 'Kwata kutaura'}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { backgroundColor: '#2E7D32', padding: 16, paddingTop: 50, alignItems: 'center' },
  headerTitle: { color: '#fff', fontSize: 20, fontWeight: 'bold' },
  headerSubtitle: { color: '#A5D6A7', fontSize: 12 },
  messageList: { flex: 1 },
  loadingContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, gap: 8 },
  loadingText: { color: '#888' },
  micContainer: { alignItems: 'center', padding: 32 },
  micButton: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#2E7D32', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  micButtonActive: { backgroundColor: '#c62828' },
  micLabel: { color: '#666', fontSize: 14 },
});

export default VoiceScreen;
