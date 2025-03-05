import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';

import CategoryScreen from '../screens/CategoryScreen';
import ProductScreen from '../screens/ProductScreen';
import CartScreen from '../screens/CartScreen';
import PaymentScreen from '../screens/PaymentScreen';
import ProductDetailScreen from '../screens/ProductDetailScreen';
import MypageScreen from '../screens/MypageScreen';
import ImageDetailScreen from '../screens/ImageDetailScreen';

import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faLayerGroup } from '@fortawesome/free-solid-svg-icons/faLayerGroup';
import { faSpinner } from '@fortawesome/free-solid-svg-icons/faSpinner';
import { faList } from '@fortawesome/free-solid-svg-icons/faList';
import { faCartShopping } from '@fortawesome/free-solid-svg-icons/faCartShopping';
import { faCreditCard } from '@fortawesome/free-solid-svg-icons/faCreditCard';
import { faUser } from '@fortawesome/free-solid-svg-icons/faUser';
import { TouchableOpacity } from 'react-native-gesture-handler';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons/faArrowLeft';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

type Product = {
  productId: string;
  categoryId: string;
  coupon: string;
  delivery: string;
  mall: string;
  name: string;
  price: number;
  rating: number;
  thumbnailCaption: string;
  thumbnailUrl: string;
}

export type RootStackParamList = {
  Category: undefined;
  Product: {
    products?: Product[];
    category?: {
      id: string;
      name: string;
    }
  } | undefined;
  ProductDetail: { 
    product?: {
      productId: string;
      coupon: string;
      delivery: string;
      mall: string;
      name: string;
      price: number;
      rating: number;
      thumbnailCaption: string;
      thumbnailUrl: string;
    },
    ImageDetail: {
      thumbnailUrl: string;
      thumbnailCaption: string;
      thumbnailCaptionShort: string;
      from: string | undefined;
    }
  };
  Payment: undefined;
  Cart: undefined;
  Mypage: undefined;
  ImageDetail: {
    thumbnailUrl: string;
    thumbnailCaption: string;
    thumbnailCaptionShort: string;
    from: string | undefined;
  };
};

const CategoryStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen
        name="Category"
        component={CategoryScreen}
        options={{
          headerShown: true,
          title: '카테고리',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          }} />
      <Stack.Screen
        name="Product"
        component={ProductScreen}
        options={({ navigation }) => ({
          headerShown: true,
          title: '상품 목록',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
        })}
      />
      <Stack.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={({ navigation }) => ({
          title: '상세정보',
          headerShown: true,
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
        })}
      />
      <Stack.Screen
        name="ImageDetail"
        component={ImageDetailScreen}
        options={({ navigation }) => ({
          title: '이미지 상세',
          headerShown: true,
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
          })}
        />
    </Stack.Navigator>
  );
};

const ProductStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true
      }}>
      <Stack.Screen
        name="Product"
        component={ProductScreen}
        options={{
          headerShown: true,
          title: '상품 목록',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          }} />
      <Stack.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={({ navigation }) => ({
          title: '상세정보',
          headerShown: true,
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
        })}
      />
      <Stack.Screen
        name="ImageDetail"
        component={ImageDetailScreen}
        options={({ navigation }) => ({
          title: '이미지 상세',
          headerShown: true,
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
          })}
        />
    </Stack.Navigator>
  );
}

const CartStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true
      }}>
      <Stack.Screen
        name="Cart"
        component={CartScreen}
        options={{
          headerShown: true,
          title: '장바구니',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          }} />
      <Stack.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={({ navigation }) => ({
          title: '상세정보',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
        })}
      />
      <Stack.Screen
        name="ImageDetail"
        component={ImageDetailScreen}
        options={({ navigation }) => ({
          title: '이미지 상세',
          headerShown: true,
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          headerLeft: () => (
            <TouchableOpacity onPress={() => navigation.goBack()} style={{ marginLeft: 16 }}>
              <FontAwesomeIcon icon={faArrowLeft} />
            </TouchableOpacity>
          ),
          })}
        />
    </Stack.Navigator>
  );
}

const MypageStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true
      }}>
      <Stack.Screen
        name="Mypage"
        component={MypageScreen}
        options={{
          headerShown: true,
          title: '내 정보',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          }} />
    </Stack.Navigator>
  );
}

const PaymentStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true
      }}>
      <Stack.Screen
        name="Payment"
        component={PaymentScreen}
        options={{
          headerShown: true,
          title: '결제',
          headerStyle: { 
            backgroundColor: '#d3e3e9',
          },
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 24,
          },
          }} />
    </Stack.Navigator>
  );
}


const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color }) => {
          let iconName = faSpinner;
          if (route.name === '카테고리') iconName = faLayerGroup;
          else if (route.name === '상품') iconName = faList;
          else if (route.name === '장바구니') iconName = faCartShopping;
          else if (route.name === '결제') iconName = faCreditCard;
          else if (route.name === '내 정보') iconName = faUser;
          return <FontAwesomeIcon icon={iconName} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="카테고리" component={CategoryStack} options={{headerShown: false}} />
      <Tab.Screen name="상품" component={ProductStack} options={{headerShown: false}} />
      <Tab.Screen name="장바구니" component={CartStack} options={{headerShown: false}} />
      <Tab.Screen name="결제" component={PaymentStack} options={{headerShown: false}} />
      <Tab.Screen name="내 정보" component={MypageStack} options={{headerShown: false}} />
    </Tab.Navigator>
  );
};

export default TabNavigator;