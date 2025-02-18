import { StyleSheet } from 'react-native';

export const categoryStyles = StyleSheet.create({
  rowContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flex: 1,
  },
  itemContainer: {
    flex: 1, // 행 내에서 동일한 공간을 차지
    margin: 8, // 항목 간 간격
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff1c9',
    borderRadius: 8,
  },
  itemIcon: {
    marginBottom: 12,
  },
  emptyItem: {
    flex: 1,
    margin: 8,
    padding: 20,
    backgroundColor: 'transparent',
    borderRadius: 8,
  },
  icon: {
    fontSize: 32,
    marginBottom: 8,
  },
  name: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});