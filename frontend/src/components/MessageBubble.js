import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Clipboard } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  if (isNaN(date.getTime())) return '';
  return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
};

const MessageBubble = ({ message, darkMode }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    Clipboard.setString(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <View style={[styles.container, isUser ? styles.userContainer : styles.assistantContainer]}>
      {!isUser && (
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>R</Text>
        </View>
      )}
      <View style={{ maxWidth: '72%' }}>
        <View style={[styles.bubble,
          isUser ? styles.userBubble :
          darkMode ? styles.assistantDark : styles.assistantLight]}>
          <Text style={[styles.text,
            isUser ? styles.userText :
            darkMode ? styles.darkText : styles.lightText]}>
            {message.content}
          </Text>
        </View>
        <View style={[styles.meta, isUser && { flexDirection: 'row-reverse' }]}>
          <Text style={styles.time}>{formatTime(message.timestamp)}</Text>
          {!isUser && (
            <TouchableOpacity onPress={handleCopy} style={styles.copyBtn}>
              <Ionicons name={copied ? 'checkmark' : 'copy-outline'} size={11} color="#888" />
              <Text style={styles.copyText}>{copied ? 'Yakopwa' : 'Kopa'}</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginVertical: 4, flexDirection: 'row', alignItems: 'flex-end', gap: 8 },
  userContainer: { justifyContent: 'flex-end' },
  assistantContainer: { justifyContent: 'flex-start' },
  avatar: { width: 26, height: 26, borderRadius: 13, backgroundColor: '#2E7D32', justifyContent: 'center', alignItems: 'center', marginBottom: 18 },
  avatarText: { color: '#fff', fontWeight: 'bold', fontSize: 11 },
  bubble: { padding: 11, borderRadius: 16 },
  userBubble: { backgroundColor: '#2E7D32', borderBottomRightRadius: 4 },
  assistantLight: { backgroundColor: '#f0f4f0', borderBottomLeftRadius: 4 },
  assistantDark: { backgroundColor: '#2a2a2a', borderBottomLeftRadius: 4 },
  text: { fontSize: 14, lineHeight: 21 },
  userText: { color: '#fff' },
  lightText: { color: '#1a1a1a' },
  darkText: { color: '#fff' },
  meta: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 2, paddingHorizontal: 4 },
  time: { fontSize: 10, color: '#aaa' },
  copyBtn: { flexDirection: 'row', alignItems: 'center', gap: 2 },
  copyText: { fontSize: 10, color: '#888' },
});

export default MessageBubble;
