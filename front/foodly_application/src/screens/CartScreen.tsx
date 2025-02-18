// screens/CartScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  FlatList,
  StyleSheet,
  LayoutChangeEvent,
  TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import axios from 'axios';
import Config from 'react-native-config';
import { RootStackParamList } from '../navigation/TabNavigator';
import styles from '../styles/styles';
import ProductPage from '../components/ProductPage';

interface Product {
  id: string;
  name: string;
  price: string;
  rating: number;
  // API에서 image URL을 반환한다면 타입을 string으로 변경 후 ProductPage에서 <Image source={{ uri: item.image }} />로 사용합니다.
  image: any;
}

type NavigationProp = StackNavigationProp<RootStackParamList, 'ProductDetail'>;

const ProductScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp>();

  // 실제 화면에 표시할 상품 데이터를 저장하는 state
  const [cartProducts, setCartProducts] = useState<Product[]>([]);
  // FlatList의 높이를 저장하는 state (페이지 전환 시 사용)
  const [flatListHeight, setFlatListHeight] = useState<number>(0);

  /**
   * 컴포넌트가 마운트될 때, 먼저 장바구니 데이터를 가져오고
   * 각 항목의 productId를 이용해 상품 상세 정보를 가져옵니다.
   */
  useEffect(() => {
    const fetchCartAndProducts = async () => {
      try {
        // 장바구니 데이터를 불러옵니다.
        const cartResponse = await axios.get(`${Config.BASE_URL}/api/user/1/cart`);
        const cartItems = cartResponse.data; // 예: [{ cartId, userId, productId, productName, quantity, addedAt }, ...]

        // 각 장바구니 항목에 대해 productId를 이용해 상품 정보를 불러옵니다.
        const productPromises = cartItems.map(async (cartItem: any) => {
          const productResponse = await axios.get(
            `${Config.BASE_URL}/api/product/${cartItem.productId}`
          );
          // productResponse.data가 Product 인터페이스와 맞는다고 가정합니다.
          return productResponse.data;
        });

        const products: Product[] = await Promise.all(productPromises);
        setCartProducts(products);
      } catch (error) {
        console.error('Error fetching cart or product data:', error);
      }
    };

    fetchCartAndProducts();
  }, []);

  /**
   * FlatList의 높이를 측정하여 페이지 단위로 정확한 높이를 지정하기 위함
   */
  const handleLayout = (event: LayoutChangeEvent) => {
    const { height } = event.nativeEvent.layout;
    setFlatListHeight(height);
  };

  /**
  * 상품 데이터를 3개씩 페이지 단위로 분할하는 함수
  */
  const chunkProducts = (products: Product[], size: number): Product[][] => {
    const chunks: Product[][] = [];
    for (let i = 0; i < products.length; i += size) {
      const chunk = products.slice(i, i + size);
      // 빈 아이템 추가: 화면 채움 용도
      while (chunk.length < size) {
        chunk.push({
          productId: `empty-${chunk.length}`,
          categoryId: '',
          name: '',
          price: '0',
          rating: 0,
          thumbnailUrl: '',
          thumbnailCaption: '',
          coupon: '',
          delivery: '',
          mall: '',
        });
      }
      chunks.push(chunk);
    }
    return chunks;
  };

  // 가져온 상품 데이터를 3개씩 페이지 단위로 나눕니다.
  const pages = chunkProducts(cartProducts, 3);

  return (
    <SafeAreaView style={styles.safeContainer}>
      <View style={styles.container}>
        {/* 상품 리스트 */}
        <View style={screenStyles.flatListContainer} onLayout={handleLayout}>
          {flatListHeight > 0 && (
            <FlatList
              data={pages}
              keyExtractor={(_, index) => `page-${index}`}
              renderItem={({ item }) => (
                <ProductPage key={item[0].id} pageData={item} screenLength={flatListHeight} />
              )}
              pagingEnabled
              decelerationRate="fast"
              showsVerticalScrollIndicator={false}
              initialNumToRender={pages.length}
            />
          )}
        </View>

        {/* "쓸어내려 더 보기" 텍스트 */}
        <Text style={screenStyles.moreText}>쓸어내려 더 보기</Text>

        {/* 결제 예상 금액 버튼 */}
        <View style={screenStyles.paymentButton}>
          <Text style={screenStyles.priceText}>결제 예상 금액</Text>
        </View>

        {/* 결제하기 버튼 */}
        <TouchableOpacity
          style={screenStyles.payButton}
          onPress={() => navigation.navigate('결제')}
        >
          <Text style={screenStyles.buttonText}>결제하기</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

export default ProductScreen;

const screenStyles = StyleSheet.create({
  flatListContainer: {
    flex: 1,
  },
  moreText: {
    textAlign: 'center',
    color: '#666',
    marginTop: 16,
    fontSize: 16,
  },
  paymentButton: {
    backgroundColor: '#fff1c9',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginTop: 16,
    height: 64,
    justifyContent: 'center',
  },
  payButton: {
    backgroundColor: '#0f5975',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    height: 64,
    justifyContent: 'center',
  },
  priceText: {
    color: '#000',
    fontSize: 24,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  buttonText: {
    color: '#fff',
    fontSize: 24,
    textAlign: 'center',
    fontWeight: 'bold',
  },
});