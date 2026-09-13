import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, FlatList,
  StyleSheet, Animated, KeyboardAvoidingView,
  Platform, Alert, Image
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import * as ImagePicker from 'expo-image-picker';
import MessageBubble from '../components/MessageBubble';
import { useChat } from '../hooks/useChat';

const SIDEBAR_FULL = 240;
const SIDEBAR_RAIL = 52;

const getGreeting = (name) => {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return `Wamuka sei, ${name}`;
  if (h >= 12 && h < 17) return `Waswera sei, ${name}`;
  return `Manheru akanaka, ${name}`;
};

const TypingIndicator = () => {
  const dots = [useRef(new Animated.Value(0)).current, useRef(new Animated.Value(0)).current, useRef(new Animated.Value(0)).current];
  useEffect(() => {
    dots.forEach((dot, i) => {
      Animated.loop(Animated.sequence([
        Animated.delay(i * 150),
        Animated.timing(dot, { toValue: -5, duration: 300, useNativeDriver: true }),
        Animated.timing(dot, { toValue: 0, duration: 300, useNativeDriver: true }),
        Animated.delay(500),
      ])).start();
    });
  }, []);
  return (
    <View style={styles.typingRow}>
      <View style={styles.typingAvatar}><Text style={styles.typingAvatarText}>R</Text></View>
      <View style={styles.typingBubble}>
        {dots.map((dot, i) => (
          <Animated.View key={i} style={[styles.dot, { transform: [{ translateY: dot }] }]} />
        ))}
      </View>
    </View>
  );
};

const ChatScreen = ({ username = 'Recall', onLogout }) => {
  const [input, setInput] = useState('');
  const [expanded, setExpanded] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [filePreview, setFilePreview] = useState(null);
  const [profilePic, setProfilePic] = useState(null);
  const sidebarAnim = useRef(new Animated.Value(SIDEBAR_FULL)).current;
  const { messages, loading, sendMessage, uploadFile } = useChat();
  const flatListRef = useRef(null);

  const toggleSidebar = () => {
    Animated.timing(sidebarAnim, {
      toValue: expanded ? SIDEBAR_RAIL : SIDEBAR_FULL,
      duration: 200,
      useNativeDriver: false,
    }).start(() => setExpanded(!expanded));
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const text = input.trim();
    setInput('');
    setFilePreview(null);
    await sendMessage(text);
  };

  const handleDocumentUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf',
               'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
               'text/plain'],
        copyToCacheDirectory: true,
      });
      if (!result.canceled && result.assets[0]) {
        const file = result.assets[0];
        setFilePreview({ name: file.name, type: 'document' });
        await uploadFile(file.uri, file.name, file.mimeType);
      }
    } catch { Alert.alert('Kukanganisa', 'Handikwanisi kuvhura faira.'); }
  };

  const handleImageUpload = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 0.8 });
      if (!result.canceled && result.assets[0]) {
        const file = result.assets[0];
        setFilePreview({ name: 'Mufananidzo', type: 'image' });
        await uploadFile(file.uri, 'image.jpg', 'image/jpeg');
      }
    } catch { Alert.alert('Kukanganisa', 'Handikwanisi kuvhura mufananidzo.'); }
  };

  const handleProfilePic = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 0.8 });
    if (!result.canceled && result.assets[0]) setProfilePic(result.assets[0].uri);
  };

  const t = {
    bg: darkMode ? '#1a1a1a' : '#ffffff',
    sidebar: darkMode ? '#111111' : '#f7f7f7',
    text: darkMode ? '#ffffff' : '#1a1a1a',
    sub: darkMode ? '#aaaaaa' : '#666666',
    border: darkMode ? '#2a2a2a' : '#e8e8e8',
    icon: darkMode ? '#cccccc' : '#444444',
  };

  const navItems = [
    { icon: 'chatbubbles-outline', label: 'Nhaurirano', sub: 'Chats' },
    { icon: 'time-outline', label: 'Nhoroondo', sub: 'History' },
    { icon: 'document-outline', label: 'Mafaira', sub: 'Files' },
    { icon: 'settings-outline', label: 'Zvigadziriso', sub: 'Settings' },
  ];

  return (
    <View style={[styles.root, { backgroundColor: t.bg }]}>

      {/* Sidebar */}
      <Animated.View style={[styles.sidebar, { width: sidebarAnim, backgroundColor: t.sidebar, borderRightColor: t.border }]}>

        {/* Toggle button always visible */}
        <View style={styles.sidebarTopRow}>
          {expanded && (
            <View style={styles.logoRow}>
              <View style={styles.logo}><Text style={styles.logoText}>R</Text></View>
              <Text style={[styles.logoLabel, { color: t.text }]}>Ruzivo</Text>
            </View>
          )}
          <TouchableOpacity onPress={toggleSidebar} style={styles.toggleBtn}>
            <Ionicons name={expanded ? 'chevron-back' : 'chevron-forward'} size={18} color={t.icon} />
          </TouchableOpacity>
        </View>

        {expanded && (
          <>
            <TouchableOpacity style={styles.newChat}>
              <Ionicons name="add" size={15} color="#fff" />
              <Text style={styles.newChatText}>Nhaurirano Itsva</Text>
            </TouchableOpacity>

            <View style={{ flex: 1 }}>
              {navItems.map((item, i) => (
                <TouchableOpacity key={i} style={styles.navItem}>
                  <Ionicons name={item.icon} size={17} color={t.icon} />
                  <View>
                    <Text style={[styles.navLabel, { color: t.text }]}>{item.label}</Text>
                    <Text style={[styles.navSub, { color: t.sub }]}>{item.sub}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>

            <View style={[styles.sidebarBottom, { borderTopColor: t.border }]}>
              <TouchableOpacity style={styles.navItem} onPress={() => setDarkMode(!darkMode)}>
                <Ionicons name={darkMode ? 'sunny-outline' : 'moon-outline'} size={17} color={t.icon} />
                <Text style={[styles.navLabel, { color: t.text }]}>{darkMode ? 'Chiedza' : 'Rima'}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.navItem} onPress={onLogout}>
                <Ionicons name="log-out-outline" size={17} color="#c62828" />
                <Text style={[styles.navLabel, { color: '#c62828' }]}>Buda</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.profileRow} onPress={handleProfilePic}>
                {profilePic
                  ? <Image source={{ uri: profilePic }} style={styles.profilePic} />
                  : <View style={styles.profilePicDefault}>
                      <Text style={styles.profilePicLetter}>{username[0].toUpperCase()}</Text>
                    </View>
                }
                <View style={{ flex: 1 }}>
                  <Text style={[styles.profileName, { color: t.text }]}>{username}</Text>
                  <Text style={[styles.profileSub, { color: t.sub }]}>Bata kuchinja mufananidzo</Text>
                </View>
              </TouchableOpacity>
            </View>
          </>
        )}

        {/* Rail icons when collapsed */}
        {!expanded && (
          <View style={styles.railIcons}>
            {navItems.map((item, i) => (
              <TouchableOpacity key={i} style={styles.railIcon}>
                <Ionicons name={item.icon} size={18} color={t.icon} />
              </TouchableOpacity>
            ))}
          </View>
        )}
      </Animated.View>

      {/* Main */}
      <View style={[styles.main, { backgroundColor: t.bg }]}>

        {messages.length === 0 ? (
          <View style={styles.greetingContainer}>
            <Text style={[styles.greetingText, { color: t.text }]}>{getGreeting(username)}</Text>
            <Text style={[styles.greetingSub, { color: t.sub }]}>Ndingakubatsira sei nhasi?</Text>
            <View style={styles.suggestionsRow}>
              {['Ndudzi yeShona', 'Tsoro', 'Ruzivo rweZimbabwe', 'Nyora nhetembo'].map((s, i) => (
                <TouchableOpacity key={i} style={[styles.suggestion, { borderColor: t.border }]}
                  onPress={() => sendMessage(s)}>
                  <Text style={[styles.suggestionText, { color: t.text }]}>{s}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => <MessageBubble message={item} darkMode={darkMode} />}
            onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
            style={styles.messageList}
            contentContainerStyle={{ paddingVertical: 12, paddingHorizontal: 60 }}
          />
        )}

        {loading && <TypingIndicator />}

        {filePreview && (
          <View style={[styles.filePreview, { backgroundColor: t.sidebar, borderColor: t.border }]}>
            <Ionicons name={filePreview.type === 'image' ? 'image-outline' : 'document-outline'} size={14} color={t.icon} />
            <Text style={[{ flex: 1, fontSize: 13, color: t.text }]}>{filePreview.name}</Text>
            <TouchableOpacity onPress={() => setFilePreview(null)}>
              <Ionicons name="close-circle-outline" size={16} color={t.sub} />
            </TouchableOpacity>
          </View>
        )}

        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.inputWrapper}>
          <View style={[styles.inputBox, { backgroundColor: t.sidebar, borderColor: t.border }]}>
            <View style={styles.inputRow}>
              <TextInput
                style={[styles.input, { color: t.text }]}
                placeholder="Nyora muShona..."
                placeholderTextColor={t.sub}
                value={input}
                onChangeText={setInput}
                multiline
                maxLength={500}
              />
              {input.trim().length > 0 && (
                <TouchableOpacity onPress={handleSend} style={styles.sendBtn} disabled={loading}>
                  <Ionicons name="arrow-up" size={15} color="#fff" />
                </TouchableOpacity>
              )}
            </View>
            <View style={styles.iconRow}>
              <TouchableOpacity onPress={handleDocumentUpload} style={styles.iconBtn}>
                <Ionicons name="attach-outline" size={19} color={t.icon} />
              </TouchableOpacity>
              <TouchableOpacity onPress={handleImageUpload} style={styles.iconBtn}>
                <Ionicons name="image-outline" size={19} color={t.icon} />
              </TouchableOpacity>
              <TouchableOpacity style={styles.iconBtn}>
                <Ionicons name="mic-outline" size={19} color={t.icon} />
              </TouchableOpacity>
              <Text style={[styles.charCount, { color: t.sub }]}>{input.length}/500</Text>
            </View>
          </View>
          <Text style={[styles.disclaimer, { color: t.sub }]}>
            Ruzivo inogona kukanganisa. Simbisa ruzivo rwakakosha.
          </Text>
        </KeyboardAvoidingView>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  root: { flex: 1, flexDirection: 'row' },
  sidebar: { borderRightWidth: 1, overflow: 'hidden', paddingTop: 16, paddingHorizontal: 10, paddingBottom: 16 },
  sidebarTopRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 },
  logoRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  logo: { width: 30, height: 30, borderRadius: 7, backgroundColor: '#2E7D32', justifyContent: 'center', alignItems: 'center' },
  logoText: { color: '#fff', fontWeight: 'bold', fontSize: 15 },
  logoLabel: { fontSize: 17, fontWeight: 'bold' },
  toggleBtn: { padding: 4, borderRadius: 6 },
  newChat: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#2E7D32', paddingVertical: 8, paddingHorizontal: 10, borderRadius: 8, gap: 6, marginBottom: 14 },
  newChatText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  navItem: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8, paddingHorizontal: 6, borderRadius: 7, marginBottom: 2 },
  navLabel: { fontSize: 13, fontWeight: '500' },
  navSub: { fontSize: 10 },
  sidebarBottom: { borderTopWidth: 1, paddingTop: 10, gap: 2 },
  profileRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingTop: 10, marginTop: 4 },
  profilePic: { width: 34, height: 34, borderRadius: 17 },
  profilePicDefault: { width: 34, height: 34, borderRadius: 17, backgroundColor: '#2E7D32', justifyContent: 'center', alignItems: 'center' },
  profilePicLetter: { color: '#fff', fontWeight: 'bold', fontSize: 13 },
  profileName: { fontSize: 13, fontWeight: '600' },
  profileSub: { fontSize: 10 },
  railIcons: { marginTop: 8, gap: 4, alignItems: 'center' },
  railIcon: { padding: 10, borderRadius: 8 },
  main: { flex: 1 },
  greetingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 40 },
  greetingText: { fontSize: 26, fontWeight: 'bold', textAlign: 'center', marginBottom: 6 },
  greetingSub: { fontSize: 15, textAlign: 'center', marginBottom: 28 },
  suggestionsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'center' },
  suggestion: { borderWidth: 1, borderRadius: 20, paddingHorizontal: 14, paddingVertical: 7 },
  suggestionText: { fontSize: 13 },
  messageList: { flex: 1 },
  typingRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 60, paddingVertical: 6 },
  typingAvatar: { width: 24, height: 24, borderRadius: 12, backgroundColor: '#2E7D32', justifyContent: 'center', alignItems: 'center' },
  typingAvatarText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  typingBubble: { flexDirection: 'row', gap: 4, backgroundColor: '#f0f0f0', padding: 10, borderRadius: 12 },
  dot: { width: 7, height: 7, borderRadius: 4, backgroundColor: '#888' },
  filePreview: { flexDirection: 'row', alignItems: 'center', marginHorizontal: 60, marginBottom: 6, padding: 8, borderRadius: 8, borderWidth: 1, gap: 8 },
  inputWrapper: { paddingHorizontal: 60, paddingBottom: 12 },
  inputBox: { borderWidth: 1, borderRadius: 14, overflow: 'hidden' },
  inputRow: { flexDirection: 'row', alignItems: 'flex-end', paddingHorizontal: 12, paddingTop: 10, paddingBottom: 4 },
  input: { flex: 1, fontSize: 14, maxHeight: 80, minHeight: 32, paddingVertical: 4, outlineStyle: 'none' },
  sendBtn: { backgroundColor: '#2E7D32', width: 28, height: 28, borderRadius: 14, justifyContent: 'center', alignItems: 'center', marginLeft: 8, marginBottom: 2 },
  iconRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 8, paddingBottom: 6 },
  iconBtn: { padding: 5 },
  charCount: { flex: 1, textAlign: 'right', fontSize: 11, paddingRight: 4 },
  disclaimer: { fontSize: 11, textAlign: 'center', marginTop: 6 },
});

export default ChatScreen;
