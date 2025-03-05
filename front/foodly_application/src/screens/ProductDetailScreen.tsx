// ProductDetailScreen.tsx
import React, { useRef, useState, useEffect } from 'react';
import Config from 'react-native-config';
import {
  View,
  Text,
  TouchableOpacity,
  Animated,
  StyleSheet,
  LayoutAnimation,
  Platform,
  UIManager,
  Dimensions,
  Image,  // 이미지 사용
} from 'react-native';
import { useRoute, RouteProp, useNavigation } from '@react-navigation/native';
import { RootStackParamList } from '../navigation/TabNavigator';
import { productDetailStyles } from '../styles/productDetailStyles';
import axios from 'axios'; // axios 추가

if (
  Platform.OS === 'android' &&
  UIManager.setLayoutAnimationEnabledExperimental
) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// =====================================
// 타입 정의(선택사항)
// =====================================
interface DescriptionResponseDTO {
  productId: number;
  summaryExp: string;
  summaryCook: string;
  summaryStore: string;
  cautionAllergy1: string;
  cautionAllergy2: string;
  cautionStore: string;
  sizeDescription: string;
  sizeImageUrl: string;
  nutrition: string;
  ingredient: string;
  reviewGoodTaste: string;
  reviewGoodTasteNum: number;
  reviewGoodDelivery: string;
  reviewGoodDeliveryNum: number;
  reviewBadTaste: string;
  reviewBadTasteNum: number;
  reviewBadDelivery: string;
  reviewBadDeliveryNum: number;
}

// =====================================
// 상수 및 애니메이션 계산용 변수
// =====================================
type RouteProps = RouteProp<RootStackParamList, 'ProductDetail'>;

const HEADER_MAX_HEIGHT = 260;
const HEADER_MIN_HEIGHT = 80;
const HEADER_SCROLL_DISTANCE = HEADER_MAX_HEIGHT - HEADER_MIN_HEIGHT;

// 기기 너비
const SCREEN_WIDTH = Dimensions.get('window').width;

// 이미지 크기 및 위치
const imageInitialSize = 220;
const imageFinalSize = 128;
const imageInitialLeft = (SCREEN_WIDTH - imageInitialSize) / 2;
const imageFinalLeft = SCREEN_WIDTH - imageFinalSize - 8;
const imageTranslateXOutput = imageFinalLeft - imageInitialLeft; // 오른쪽 이동량

// 텍스트 컨테이너 기본 값
const textContainerMargin = 16;
const textContainerWidth = SCREEN_WIDTH - 2 * textContainerMargin;
const textInitialLeft = textContainerMargin; // 초기 좌측 여백 16
const textTranslateYOutput = 106 - imageInitialSize;

// 애니메이션 설정
const animatedNameFont = (scrollY: Animated.Value) =>
  scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [28, 20],
    extrapolate: 'clamp',
  });

const animatedInfoFont = (scrollY: Animated.Value) =>
  scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [20, 20],
    extrapolate: 'clamp',
  });

const animatedProductNameBottomMargin = (scrollY: Animated.Value) =>
  scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE * 0.5, HEADER_SCROLL_DISTANCE],
    outputRange: [12, 9, 6],
    extrapolate: 'clamp',
  });

const animatedPriceBottomMargin = (scrollY: Animated.Value) =>
  scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE * 0.5, HEADER_SCROLL_DISTANCE],
    outputRange: [8, 4, 0],
    extrapolate: 'clamp',
  });

const textTranslateY = (scrollY: Animated.Value) =>
  scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [0, textTranslateYOutput - 28],
    extrapolate: 'clamp',
  });

// 텍스트 컨테이너의 width 애니메이션 (초기: textContainerWidth, 최종: 70% 정도)
const animatedTextContainerWidth = (scrollY: Animated.Value) =>
  scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [textContainerWidth, textContainerWidth * 0.6],
    extrapolate: 'clamp',
  });

const ProductDetailScreen: React.FC = ({ route }) => {
  const navigation = useNavigation();
  const { product } = route.params;
  const [isScrolled, setIsScrolled] = useState(false);

  // 스크롤 애니메이션 값
  const scrollY = useRef(new Animated.Value(0)).current;

  // =====================================
  // 상품 상세 내용(Description) 로딩
  // =====================================
  const [description, setDescription] = useState<DescriptionResponseDTO | null>(null);

  useEffect(() => {
    axios
      .get<DescriptionResponseDTO>(`${Config.BASE_URL}/api/descriptions/${product?.productId}`)
      .then(res => {
        console.log(res.data);
        setDescription(res.data);
      })
      .catch(err => {
        console.error(err);
      });
  }, [product?.productId]);

  // =====================================
  // 아코디언에 보여줄 버튼/컨텐츠 구성
  // =====================================
  const ACCORDION_ITEMS = [
    // 1) 상품 설명 (상품 설명 + 조리 방법)
    { id: 1, title: '상품 설명' },
    // 2) 주의사항 (1차 알레르기, 2차 알레르기, 보관 유의사항)
    { id: 4, title: '주의사항' },
    // 3) 크기 정보 (이미지 + size 텍스트)
    { id: 5, title: '크기 정보' },
    // 4) 영양/성분 정보 (영양 정보 + 성분 정보)
    { id: 6, title: '영양/성분 정보' },
    // 5) 리뷰 요약 (높은 리뷰 요약 + 낮은 리뷰 요약)
    { id: 8, title: '리뷰 요약' },
  ];

  // 스크롤 이벤트 리스너
  useEffect(() => {
    const listener = scrollY.addListener(({ value }) => {
      value > 0 ? setIsScrolled(true) : setIsScrolled(false);
    });
    return () => {
      scrollY.removeListener(listener);
    };
  }, []);

  // 헤더 높이 애니메이션
  const headerHeight = scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [HEADER_MAX_HEIGHT, HEADER_MIN_HEIGHT],
    extrapolate: 'clamp',
  });

  // 이미지 애니메이션
  const imageTranslateX = scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [0, imageTranslateXOutput],
    extrapolate: 'clamp',
  });
  const imageSizeAnim = scrollY.interpolate({
    inputRange: [0, HEADER_SCROLL_DISTANCE],
    outputRange: [imageInitialSize, imageFinalSize],
    extrapolate: 'clamp',
  });

  // 아코디언 확장 여부
  const [expandedSection, setExpandedSection] = useState<number | null>(null);
  const toggleSection = (id: number) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedSection(prev => (prev === id ? null : id));
  };

  // =====================================
  // 각 아코디언 아이템별 커스텀 컨텐츠 렌더링
  // =====================================

  // id=1: 상품 설명 + 조리 방법
  const renderItem1Content = () => {
    return (
      <View>
        <Text style={localStyles.bigHeadline}>상품 설명</Text>
        <Text style={localStyles.paragraph}>
          {description?.summaryExp || '상품 설명 정보가 없습니다.'}
        </Text>

        {/* 조리 방법이 있을 때만 */}
        {description?.summaryCook && (
          <>
            <Text style={localStyles.bigHeadline}>조리 방법</Text>
            <Text style={localStyles.paragraph}>
              {description?.summaryCook || '조리 방법 정보가 없습니다.'}
            </Text>
          </>
        )}
      </View>
    );
  };

  // id=4: 주의사항 (1차 알레르기, 2차 알레르기, 보관 유의사항)
  const renderItem4Content = () => {
    return (
      <View>
        <Text style={localStyles.bigHeadline}>1차 알레르기</Text>
        <Text style={localStyles.paragraph}>
          {description?.cautionAllergy1 ?? '유발 성분이 없습니다.'}
        </Text>

        <Text style={localStyles.bigHeadline}>2차 알레르기</Text>
        <Text style={localStyles.paragraph}>
          {description?.cautionAllergy2 ?? '유발 성분이 없습니다.'}
        </Text>

        <Text style={localStyles.bigHeadline}>보관 유의사항</Text>
        <Text style={localStyles.paragraph}>
          {description?.cautionStore ?? '없습니다.'}
        </Text>
      </View>
    );
  };

  // id=5: 크기 정보 (이미지 + size 텍스트)
  const renderItem5Content = () => {
    return (
      <View>
        {/* 이미지가 있는 경우만 표시 (없다면 기본 텍스트 대체 가능) */}
        {description?.sizeImageUrl ? (
          <Image
            style={{
              width: '100%',
              height: 200,
              resizeMode: 'contain',
              marginBottom: 8,
            }}
            source={{ uri: description.sizeImageUrl }}
          />
        ) : (
          <Text style={localStyles.paragraph}>
            이미지 정보가 없습니다.
          </Text>
        )}

        {/* 크기 정보 */}
        <Text style={localStyles.paragraph}>
          {description?.sizeDescription || '크기 정보가 없습니다.'}
        </Text>
      </View>
    );
  };

  // id=6: 영양/성분 정보 (영양 정보 + 성분 정보)
  const renderItem6Content = () => {
    return (
      <View>
        <Text style={localStyles.bigHeadline}>영양 정보</Text>
        <Text style={localStyles.paragraph}>
          {description?.nutrition || '영양 정보가 없습니다.'}
        </Text>

        <Text style={localStyles.bigHeadline}>성분 정보</Text>
        <Text style={localStyles.paragraph}>
          {description?.ingredient || '성분 정보가 없습니다.'}
        </Text>
      </View>
    );
  };

  // id=8: 리뷰 요약 (높은 리뷰 요약 + 낮은 리뷰 요약)
  const renderItem8Content = () => {
    if (!description?.reviewGoodTasteNum) {
      return (
        <View>
          <Text style={localStyles.paragraph}>
            리뷰 요약 정보는 현재 준비중입니다.
          </Text>
        </View>
      )
    }

    return (
      <View>
        {/* 높은 리뷰 요약 */}
        <View style={localStyles.greyHeaderContainer}>
          <Text style={localStyles.greyHeaderText}>높은 리뷰 요약</Text>
        </View>
        {/* 맛 */}
        <Text style={localStyles.bigHeadline}>
          맛 ({description?.reviewGoodTasteNum ?? 0}개)
        </Text>
        <Text style={localStyles.paragraph}>
          {description?.reviewGoodTaste || '-'}
        </Text>
        {/* 배송 */}
        <Text style={localStyles.bigHeadline}>
          배송 ({description?.reviewGoodDeliveryNum ?? 0}개)
        </Text>
        <Text style={localStyles.paragraph}>
          {description?.reviewGoodDelivery || '-'}
        </Text>

        {/* 낮은 리뷰 요약 */}
        <View style={[localStyles.greyHeaderContainer, { marginTop: 16 }]}>
          <Text style={localStyles.greyHeaderText}>낮은 리뷰 요약</Text>
        </View>
        {/* 맛 */}
        <Text style={localStyles.bigHeadline}>
          맛 ({description?.reviewBadTasteNum ?? 0}개)
        </Text>
        <Text style={localStyles.paragraph}>
          {description?.reviewBadTaste || '-'}
        </Text>
        {/* 배송 */}
        <Text style={localStyles.bigHeadline}>
          배송 ({description?.reviewBadDeliveryNum ?? 0}개)
        </Text>
        <Text style={localStyles.paragraph}>
          {description?.reviewBadDelivery || '-'}
        </Text>
      </View>
    );
  };

  // 아코디언 공통 렌더링 함수
  const renderAccordionContent = (itemId: number) => {
    switch (itemId) {
      case 1:
        return renderItem1Content();
      case 4:
        return renderItem4Content();
      case 5:
        return renderItem5Content();
      case 6:
        return renderItem6Content();
      case 8:
        return renderItem8Content();
      default:
        return <Text>해당 섹션 정보가 없습니다.</Text>;
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: '#fff' }}>
      {/* 애니메이션 헤더 */}
      <Animated.View style={{ maxHeight: 160 }}>
        {/* 이미지 영역 */}
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={() =>
            navigation.navigate('ImageDetail', {
              thumbnailUrl: product?.thumbnailUrl,
              thumbnailCaption: product?.thumbnailCaption,
              thumbnailCaptionShort: product?.thumbnailCaptionShort,
              from: 'ProductDetail',
            })
          }
        >
          <Animated.View
            style={{
              top: 16,
              left: imageInitialLeft,
              transform: [{ translateX: imageTranslateX }],
            }}
          >
            <Animated.Image
              source={{ uri: product?.thumbnailUrl }}
              style={{
                width: imageSizeAnim,
                height: imageSizeAnim,
                borderRadius: 8,
                resizeMode: 'contain',
              }}
            />
          </Animated.View>
        </TouchableOpacity>

        {/* 텍스트 영역 */}
        <Animated.View
          style={{
            top: 32,
            left: textInitialLeft,
            width: animatedTextContainerWidth(scrollY),
            transform: [{ translateY: textTranslateY(scrollY) }],
          }}
        >
          {/* 제품명 */}
          <Animated.Text
            style={[
              productDetailStyles.name,
              {
                fontSize: animatedNameFont(scrollY),
                marginBottom: animatedProductNameBottomMargin(scrollY),
              },
            ]}
          >
            {product?.name}
          </Animated.Text>

          {/* 가격 정보 */}
          <Animated.View
            style={[
              productDetailStyles.mallpriceContainer,
              { marginBottom: animatedPriceBottomMargin(scrollY) },
            ]}
          >
            <Animated.Text
              style={[
                productDetailStyles.mall,
                { fontSize: animatedInfoFont(scrollY) },
              ]}
            >
              이마트몰
            </Animated.Text>
            <View style={productDetailStyles.priceContainer}>
              {!isScrolled && (
                <Animated.Text style={productDetailStyles.beforePrice}>
                  {(product?.price * 1.2).toLocaleString()}원에서
                </Animated.Text>
              )}
              <Animated.Text style={productDetailStyles.price}>
                {product?.price.toLocaleString()}원
              </Animated.Text>
            </View>
          </Animated.View>

          {/* 별점 정보 (예시로 고정 값) */}
          <View style={productDetailStyles.ratingContainer}>
            <Animated.Text
              style={[
                productDetailStyles.rating,
                { fontSize: animatedInfoFont(scrollY) },
              ]}
            >
              {product.rating} / 5점
            </Animated.Text>
            <Animated.Text
              style={[
                productDetailStyles.rating,
                { fontSize: animatedInfoFont(scrollY) },
              ]}
            >
              건의 리뷰
            </Animated.Text>
          </View>
        </Animated.View>
      </Animated.View>

      {/* 스크롤 영역 */}
      <Animated.ScrollView
        contentContainerStyle={{ paddingTop: HEADER_MAX_HEIGHT }}
        scrollEventThrottle={16}
        onScroll={Animated.event(
          [{ nativeEvent: { contentOffset: { y: scrollY } } }],
          { useNativeDriver: false }
        )}
      >
        <View style={{ paddingHorizontal: 16 }}>
          {/* 할인 버튼 */}
          <View style={productDetailStyles.discountButton}>
            <Text style={productDetailStyles.discount}>
              {product?.coupon}
            </Text>
          </View>

          {/* 배송 버튼 */}
          <View style={[productDetailStyles.deliveryButton, { marginTop: 10 }]}>
            <Text style={productDetailStyles.delivery}>
              {product?.delivery}
            </Text>
          </View>

          {/* 아코디언 버튼들 */}
          <View style={{ marginTop: 20 }}>
            {ACCORDION_ITEMS.map(item => {
              const isExpanded = expandedSection === item.id;
              return (
                <View key={item.id} style={{ marginBottom: 12 }}>
                  <TouchableOpacity
                    style={localStyles.accordionButton}
                    onPress={() => toggleSection(item.id)}
                  >
                    <Text style={localStyles.accordionButtonText}>
                      {item.title}
                    </Text>
                  </TouchableOpacity>
                  {isExpanded && (
                    <View style={localStyles.accordionContent}>
                      {renderAccordionContent(item.id)}
                    </View>
                  )}
                </View>
              );
            })}
          </View>

          {/* 하단 여백 (고정 버튼이 가리지 않도록) */}
          <View style={{ height: 120 }} />
        </View>
      </Animated.ScrollView>

      {/* 하단 고정 버튼 */}
      <View style={productDetailStyles.bottomFixedContainer}>
        <TouchableOpacity
          style={[productDetailStyles.cartButton, { marginRight: 8, flex: 1 }]}
          onPress={() => console.log('장바구니 클릭')}
        >
          <Text style={productDetailStyles.buttonText}>장바구니</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[productDetailStyles.buyButton, { flex: 1 }]}
          onPress={() => navigation.navigate('결제')}
        >
          <Text style={productDetailStyles.buttonText}>구매</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default ProductDetailScreen;


// ================== 로컬 스타일 ==================
const localStyles = StyleSheet.create({
  headerContainer: {
    backgroundColor: '#fff',
  },
  accordionButton: {
    backgroundColor: '#FFF1C9',
    height: 60,
    padding: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  accordionButtonText: {
    fontSize: 24,
    fontWeight: 'bold',
    alignSelf: 'center',
  },
  accordionContent: {
    backgroundColor: '#FFF9E7',
    padding: 12,
    borderRadius: 8,
  },
  // 기본 텍스트
  accordionContentText: {
    fontSize: 20,
    lineHeight: 24,
    marginTop: 8,
    marginBottom: 8,
  },
  // 대제목
  bigHeadline: {
    fontSize: 22,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  // 일반 단락
  paragraph: {
    fontSize: 18,
    lineHeight: 24,
    marginBottom: 12,
  },
  // 회색 헤더
  greyHeaderContainer: {
    backgroundColor: '#d9d9d9',
    paddingVertical: 8,
    borderRadius: 8,
    marginBottom: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  greyHeaderText: {
    fontSize: 22,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});