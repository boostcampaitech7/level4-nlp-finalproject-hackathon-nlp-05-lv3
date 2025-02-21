// screens/ImageDetailScreen.tsx
import React from 'react';
import { View, Text, Image, StyleSheet, SafeAreaView } from 'react-native';
import { StackScreenProps } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/TabNavigator';

type ImageDetailScreenProps = StackScreenProps<RootStackParamList, 'ImageDetail'>;

const ImageDetailScreen: React.FC<ImageDetailScreenProps> = ({ route }) => {
  const { thumbnailUrl, thumbnailCaption } = route.params;

  return (
    <SafeAreaView style={styles.container}>
      <Image
        source={{ uri: thumbnailUrl }}
        style={styles.image}
        // accessibilityLabel를 통해 스크린리더(VoiceOver/토크백 등)에서 읽히는 텍스트로 활용
        accessibilityLabel={thumbnailCaption || '상품 이미지'}
      />
      <Text style={styles.caption}>{thumbnailCaption}</Text>
    </SafeAreaView>
  );
};

export default ImageDetailScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: 300,
    height: 300,
    resizeMode: 'contain',
  },
  caption: {
    marginTop: 16,
    fontSize: 20,
    marginHorizontal: 16,
    textAlign: 'center',
  },
});