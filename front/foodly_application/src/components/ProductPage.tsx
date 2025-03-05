// components/ProductPage.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  LayoutChangeEvent,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/TabNavigator';
import { productStyles } from '../styles/productStyles';

interface Product {
  productId: string;
  coupon: string;
  delivery: string;
  mall: string;
  name: string;
  price: number;
  rating: number;
  thumbnailCaption: string;
  thumbnailCaptionShort: string;
  thumbnailUrl: string;
}

interface PageProps {
  pageData: Product[];     // 현재 페이지에 표시할 상품 리스트
  screenLength: number;    // 화면(또는 컨테이너) 세로 길이
}

type NavigationProp = StackNavigationProp<RootStackParamList, 'Product'>;

const ProductPage: React.FC<PageProps> = ({ pageData, screenLength }) => {
  const navigation = useNavigation<NavigationProp>();

  // 첫 번째 카드(실제 상품) 높이를 측정해서 저장
  const [cardHeight, setCardHeight] = useState<number | null>(null);

  // 3개 아이템일 때만 계산을 통해 gap을 구하고,
  // 아이템이 1개나 2개라면 gap 대신 고정 margin(예: 10) 사용
  const computedGap = (() => {
    if (cardHeight && pageData.length === 3) {
      // (화면 세로 길이 - 카드3개 높이) / (간격 2개)
      // 보통 3개의 카드면 사이가 2군데이므로 아래처럼 나눠줌
      const gap = (screenLength - 3 * cardHeight) / 2;
      return gap > 0 ? gap : 0;
    }
    // 3개가 아닌 경우는 고정 margin 사용
    return 10;
  })();

  return (
    <View style={productStyles.pageContainer}>
      {pageData.map((product, index) => {
        const isLast = index === pageData.length - 1;

        // onLayout: 첫 번째 ‘실제 상품’ 카드에서만 높이 측정
        const onCardLayout = (event: LayoutChangeEvent) => {
          if (!cardHeight && product.name) {
            const { height } = event.nativeEvent.layout;
            setCardHeight(height);
          }
        };

        // 만약 product.name이 없어서 “빈 아이템”을 채우는 경우라면
        // (이 로직이 필요 없으시면 제거하셔도 됩니다)
        if (!product.name) {
          return (
            <View
              key={product.productId}
              style={[
                productStyles.emptyItem,
                { marginBottom: isLast ? 0 : computedGap },
              ]}
              onLayout={onCardLayout}
            />
          );
        }

        // 실제 상품 카드
        return (
          <TouchableOpacity
            key={product.productId}
            style={[
              productStyles.productCard,
              { marginBottom: isLast ? 0 : computedGap },
            ]}
            // 카드 전체를 누르면 ProductDetail 스크린으로 이동
            onPress={() => navigation.navigate('ProductDetail', { product })}
            onLayout={onCardLayout}
          >
            <View style={productStyles.productInfo}>
              <Text style={productStyles.productName}>{product.name}</Text>
              <Text style={productStyles.productPrice}>
                {product.price.toLocaleString()}원
              </Text>
              <Text style={productStyles.productRating}>
                {product.rating} / 5점
              </Text>
            </View>

            {product.thumbnailUrl ? (
              // 이미지를 따로 TouchableOpacity로 감싸 이미지 부분 클릭시 ImageDetail 이동
              <TouchableOpacity
                onPress={() =>
                  navigation.navigate('ImageDetail', {
                    thumbnailUrl: product.thumbnailUrl.replace(/\?type=m510$/, ''),
                    thumbnailCaption: product.thumbnailCaption,
                    thumbnailCaptionShort: product.thumbnailCaptionShort,
                    from: undefined,
                  })
                }
              >
                <Image
                  source={{
                    uri: product.thumbnailUrl.replace(/\?type=m510$/, ''),
                  }}
                  style={productStyles.productImage}
                  accessibilityLabel={product.thumbnailCaptionShort || '상품 이미지'}
                />
              </TouchableOpacity>
            ) : (
              <View style={productStyles.placeholderImage} />
            )}
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

export default ProductPage;