import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

import styles from '../styles/styles';
import { mypageStyles } from '../styles/mypageStyles';

const MyPageScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      {/* Profile Section */}
      <View style={mypageStyles.profileContainer}>
        <Image
          source={require('../assets/image.png')}
          style={mypageStyles.profileImage}
        />
        <Text style={mypageStyles.userName}>오수현 님</Text>
      </View>

      {/* Info Update Buttons */}
      <Text style={mypageStyles.bigTitle}>정보 수정</Text>
      <TouchableOpacity style={mypageStyles.infoButton}>
        <Text style={mypageStyles.buttonText}>배송지 수정</Text>
      </TouchableOpacity>
      <TouchableOpacity style={mypageStyles.infoButton}>
        <Text style={mypageStyles.buttonText}>결제정보 수정</Text>
      </TouchableOpacity>

      {/* Logout Button */}
      <TouchableOpacity style={mypageStyles.logoutButton}>
        <Text style={mypageStyles.logoutText}>로그아웃</Text>
      </TouchableOpacity>
    </View>
  );
};

export default MyPageScreen;