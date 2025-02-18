import { StyleSheet } from 'react-native';

export const mypageStyles = StyleSheet.create({
  profileContainer: {
    display: 'flex',
    flexDirection: 'row',
    marginBottom: 20,
    borderRadius: 8,
  },
  profileImage: {
    width: 150,
    height: 150,
    marginBottom: 10,
  },
  userName: {
    marginTop: 20,
    marginLeft: 20,
    fontSize: 28,
    fontWeight: 'bold',
  },
  bigTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  infoButton: {
    backgroundColor: '#FFECB3',
    height: 60,
    marginVertical: 5,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: '#D32F2F',
    height: 60,
    marginTop: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'absolute',
    bottom: 12,
    left: 12,
    right: 12,
  },
  logoutText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});