import { StyleSheet } from 'react-native';

export const productStyles = StyleSheet.create({
  pageContainer: {
    flex: 1,
    justifyContent: 'space-between',
    paddingHorizontal: 4,
  },
  filterScroll: {
    maxHeight: 44,
  },
  filterButton: {
    backgroundColor: '#f0f0f0',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 24,
    marginRight: 10,
    justifyContent: 'center',
  },
  filterText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  flatListContainer: {
    flex: 1,
    marginTop: 20,
  },
  productInfo: {
    flex: 2,
  },
  productCard: {
    flex: 1, // 각 상품이 1/3 높이를 차지
    flexDirection: 'row',
    borderRadius: 8,
    minHeight: 160,
  },
  productName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 4,
    marginBottom: 4,
    paddingRight: 8,
  },
  productPrice: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0F5975',
  },
  productRating: {
    fontSize: 24,
    color: '#888',
  },
  productImage: {
    width: 148,
    height: 148,
    resizeMode: 'contain',
    borderRadius: 8,
  },
  placeholderImage: {
    flex: 1,
    width: 80,
    height: 80,
    backgroundColor: '#ddd',
    borderRadius: 8,
  },
  emptyItem: {
    flex: 1,
    marginVertical: 5,
    backgroundColor: 'transparent',
  }
});