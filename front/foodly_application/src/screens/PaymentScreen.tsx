import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';

import styles from '../styles/styles';
import { paymentStyles } from '../styles/paymentStyles';

const paymentData = [
  {
    id: '1',
    date: '2025-02-01',
    description: '상주곶감... 외 5',
    amount: '1,212,220원',
  },
  {
    id: '2',
    date: '2025-02-01',
    description: '상주곶감... 외 5',
    amount: '1,212,220원',
  },
];

const PaymentScreen: React.FC = () => {
  const renderItem = ({ item }) => (
    <View style={paymentStyles.itemContainer}>
      <View>
        <Text style={paymentStyles.date}>{item.date}</Text>
        <Text style={paymentStyles.description}>{item.description}</Text>
      </View>
      <Text style={paymentStyles.amount}>{item.amount}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Payment History List */}
      <FlatList data={paymentData} renderItem={renderItem} keyExtractor={(item) => item.id} />
    </View>
  );
};

export default PaymentScreen;
