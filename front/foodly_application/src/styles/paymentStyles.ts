import { StyleSheet } from 'react-native';

export const paymentStyles = StyleSheet.create({
  itemContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
  },
  date: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  amount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#005A82',
  },
  description: {
    fontSize: 24,
    color: '#555',
  },
});