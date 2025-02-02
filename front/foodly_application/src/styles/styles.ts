import { StyleSheet } from 'react-native';

export default StyleSheet.create({
  // container
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 12,
  },
  safeContainer: {
    flex: 1,
    backgroundColor: '#F0F8FF',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },

  // search
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderColor: '#CCCCCC',
    borderWidth: 1,
    borderRadius: 64,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginBottom: 16,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 40,
    marginLeft: 8,
    fontSize: 16,
  },

  // slide to see more
  moreText: {
    textAlign: 'center',
    color: '#666',
    marginTop: 16,
    fontSize: 16,
  },
});