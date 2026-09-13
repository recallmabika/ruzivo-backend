import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

export const startRecording = async () => {
  await Audio.requestPermissionsAsync();
  await Audio.setAudioModeAsync({
    allowsRecordingIOS: true,
    playsInSilentModeIOS: true,
  });
  const { recording } = await Audio.Recording.createAsync(
    Audio.RecordingOptionsPresets.HIGH_QUALITY
  );
  return recording;
};

export const stopRecording = async (recording) => {
  await recording.stopAndUnloadAsync();
  await Audio.setAudioModeAsync({ allowsRecordingIOS: false });
  return recording.getURI();
};

export const playAudioFromBytes = async (arrayBuffer) => {
  const base64 = btoa(
    new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
  );
  const uri = FileSystem.cacheDirectory + 'tts_response.wav';
  await FileSystem.writeAsStringAsync(uri, base64, { encoding: FileSystem.EncodingType.Base64 });
  const { sound } = await Audio.Sound.createAsync({ uri });
  await sound.playAsync();
  return sound;
};
