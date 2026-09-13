import React from 'react';
import { View } from 'react-native';
import ChatScreen from '../screens/ChatScreen';

const MainApp = ({ onLogout, username }) => {
  return (
    <View style={{ flex: 1 }}>
      <ChatScreen username={username} onLogout={onLogout} />
    </View>
  );
};

export default MainApp;
