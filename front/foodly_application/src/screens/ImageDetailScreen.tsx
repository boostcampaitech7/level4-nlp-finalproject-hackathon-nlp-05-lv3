// screens/ImageDetailScreen.tsx
import React, { useLayoutEffect } from 'react';
import { View, Text, Image, StyleSheet, SafeAreaView } from 'react-native';
import { StackScreenProps } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/TabNavigator';

type ImageDetailScreenProps = StackScreenProps<RootStackParamList, 'ImageDetail'>;

const ImageDetailScreen: React.FC<ImageDetailScreenProps> = ({ route, navigation }) => {
  const { thumbnailUrl, thumbnailCaption, thumbnailCaptionShort, from } = route.params;

  const caption = () => {
    if (from === 'ProductDetail') {
      console.log("from ProductDetail", thumbnailCaption);
      return thumbnailCaption;
    }
    console.log("not from ProductDetail", thumbnailCaptionShort);
    return thumbnailCaptionShort;
  }

  useLayoutEffect(() => {
    navigation.setOptions({
      title: from === 'ProductDetail' ? '포장 설명' : '제품 이미지 소개',
    });
  }, [navigation, from]);
  
  return (
    <SafeAreaView style={styles.container}>
      <Image
        source={{ uri: thumbnailUrl }}
        style={styles.image}
        accessibilityLabel={caption() || '상품 이미지'}
      />
      <Text style={styles.caption}>{caption()}</Text>
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