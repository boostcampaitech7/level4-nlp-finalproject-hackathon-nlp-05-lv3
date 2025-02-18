// screens/ProductScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  FlatList,
  LayoutChangeEvent,
  TouchableOpacity,
} from 'react-native';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';

import ProductPage from '../components/ProductPage';
import styles from '../styles/styles';
import { productStyles } from '../styles/productStyles';
import { StackScreenProps } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/TabNavigator';
import Config from 'react-native-config';

// 상품 데이터 인터페이스
export interface Product {
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

// 필터 데이터 인터페이스
export interface Filter {
  id: string;
  aspect: string;
}

// 랭크 조회 API에서 반환하는 데이터 인터페이스
export interface ProductRankResponse {
  productRankId: number;
  productId: number;
  aspectId: number;
  categoryId: number;
  productRank: number;
}

// fallback용 더미 상품 목록 (필요시 사용)
const dummyProducts: Product[] = [
  {
    productId: '1',
    categoryId: '1',
    name: '상품명',
    price: 1360,
    rating: 4.87,
    thumbnailUrl: '../assets/image.png',
    thumbnailCaption: '상품 설명',
    coupon: '쿠폰 설명',
    delivery: '배송 설명',
    mall: '판매점',
  },
];

type ProductScreenProps = StackScreenProps<RootStackParamList, 'Product'>;

const ProductScreen: React.FC<ProductScreenProps> = ({ route }) => {
  // FlatList의 높이 (페이지 단위 스크롤에 사용)
  const [flatListHeight, setFlatListHeight] = useState<number>(0);
  // 필터 관련 상태
  const [filters, setFilters] = useState<Filter[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [originalProducts, setOriginalProducts] = useState<Product[]>([]);
  const [activeFilterId, setActiveFilterId] = useState<string | null>(null);

  // ★ 검색 관련 상태 추가
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // 전달받은 상품 데이터가 있으면 우선 사용
  const passedProducts = route.params?.products;

  // 초기 상품 목록 설정 (전달받은 데이터 또는 API 호출)
  useEffect(() => {
    if (passedProducts && passedProducts.length > 0) {
      setProducts(passedProducts);
      setOriginalProducts(passedProducts);
    } else {
      axios.get(`${Config.BASE_URL}/api/product`)
        .then(response => {
          const data: Product[] = response.data;
          if (Array.isArray(data) && data.length > 0) {
            setProducts(data);
            setOriginalProducts(data);
          } else {
            setProducts(dummyProducts);
            setOriginalProducts(dummyProducts);
          }
        })
        .catch(error => {
          console.error('상품 데이터를 가져오는 중 오류 발생:', error);
          setProducts(dummyProducts);
          setOriginalProducts(dummyProducts);
        });
    }
  }, [passedProducts]);

  /**
   * FlatList의 높이를 측정하여 각 페이지의 높이를 결정합니다.
   */
  const handleLayout = (event: LayoutChangeEvent) => {
    const { height } = event.nativeEvent.layout;
    setFlatListHeight(height);
  };

  /**
   * 상품 데이터를 3개씩 페이지 단위로 분할하는 함수
   * (빈 아이템을 추가하여 한 페이지를 항상 3개로 맞춤)
   */
  const chunkProducts = (data: Product[], size: number): Product[][] => {
    const chunks: Product[][] = [];
    for (let i = 0; i < data.length; i += size) {
      const chunk = data.slice(i, i + size);
      // 화면을 채우기 위해 빈 아이템 추가 (필요 시)
      while (chunk.length < size) {
        chunk.push({
          productId: `empty-${chunk.length}`,
          categoryId: '',
          name: '',
          price: 0,
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

  // 기본 상품 목록과 검색 결과를 3개씩 분할
  const pages = chunkProducts(products, 3);
  const searchPages = chunkProducts(searchResults, 3);

  // categoryId는 route.params에서 전달받는다고 가정 (필요시 수정)
  const categoryId = route.params?.category?.id;

  // 필터 데이터 가져오기 (예: 카테고리별 필터)
  useEffect(() => {
    const fetchFilters = async () => {
      if (!categoryId) return;
      try {
        const response = await axios.get(
          `${Config.BASE_URL}/api/category/${categoryId}/aspects`
        );
        const data: Filter[] = response.data;
        setFilters(Array.isArray(data) && data.length > 0 ? data : []);
      } catch (error) {
        console.error('필터 데이터를 가져오는 중 오류 발생:', error);
        setFilters([]);
      }
    };
    fetchFilters();
  }, [categoryId]);

  /**
   * 필터 버튼 클릭 시 처리 함수
   */
  const handleFilterPress = async (filter: Filter) => {
    // 이미 활성화된 필터를 누른 경우 해제
    if (activeFilterId === filter.id) {
      setActiveFilterId(null);
      setProducts(originalProducts);
      return;
    }

    try {
      setActiveFilterId(filter.id);
      const aspectId = parseInt(filter.id, 10);

      // 1. 랭크 데이터 조회
      const rankResponse = await axios.get(
        `${Config.BASE_URL}/api/rank/aspect/${aspectId}`
      );
      const rankList: ProductRankResponse[] = rankResponse.data;
      console.log('rankList', rankList);

      // 2. 각 productId를 통해 개별 상품 조회
      const productPromises = rankList.map(rank =>
        axios.get(`${Config.BASE_URL}/api/product/${rank.productId}`)
      );
      const productResponses = await Promise.all(productPromises);
      const sortedProducts: Product[] = productResponses.map(response => response.data);

      setProducts(sortedProducts);
    } catch (error) {
      console.error('필터 정렬 데이터를 가져오는 중 오류 발생:', error);
    }
  };

  /**
   * 검색 함수: 검색어가 있으면 검색 API를 호출하여 결과를 받아옵니다.
   */
  const handleSearch = () => {
    if (!searchTerm.trim()) {
      // 검색어가 없으면 검색 모드를 해제하고 원래 목록을 사용
      setIsSearching(false);
      setSearchResults([]);
      return;
    }
    setIsSearching(true);
    axios
      .get(`${Config.BASE_URL}/api/product/search`, {
        params: { name: searchTerm },
      })
      .then(response => {
        console.log('Search results:', response.data);
        setSearchResults(response.data);
      })
      .catch(error => {
        console.error('Error searching products:', error);
      });
  };

  return (
    <SafeAreaView style={styles.safeContainer}>
      <View style={styles.container}>
        {/* 검색창 */}
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="궁금한 상품을 검색해보세요"
            value={searchTerm}
            onChangeText={setSearchTerm}
            onSubmitEditing={handleSearch}
          />
          <TouchableOpacity onPress={handleSearch}>
            <FontAwesomeIcon
              icon={faMagnifyingGlass}
              style={styles.searchIcon}
            />
          </TouchableOpacity>
        </View>

        {/* 검색 모드가 아닐 때만 필터 버튼 표시 */}
        {!isSearching && filters.length > 0 && (
          <FlatList
            data={filters}
            keyExtractor={(item) => `filter-${item.id}`}
            horizontal
            showsHorizontalScrollIndicator={false}
            style={productStyles.filterScroll}
            renderItem={({ item }) => {
              const isActive = activeFilterId === item.id;
              return (
                <TouchableOpacity
                  style={[
                    productStyles.filterButton,
                    isActive && { backgroundColor: '#FFA500' },
                  ]}
                  onPress={() => handleFilterPress(item)}
                >
                  <Text
                    style={[
                      productStyles.filterText,
                      isActive && { color: '#ffffff' },
                    ]}
                  >
                    {item.aspect}
                  </Text>
                </TouchableOpacity>
              );
            }}
          />
        )}

        {/* 상품 리스트 또는 검색 결과 (한 페이지에 3개씩, 스크롤로 페이지 이동) */}
        <View style={productStyles.flatListContainer} onLayout={handleLayout}>
          {flatListHeight > 0 && (
            <FlatList
              data={isSearching ? searchPages : pages}
              keyExtractor={(_, index) =>
                isSearching ? `search-page-${index}` : `page-${index}`
              }
              renderItem={({ item }) => (
                <ProductPage
                  pageData={item}
                  screenLength={flatListHeight}
                />
              )}
              pagingEnabled
              decelerationRate="fast"
              showsVerticalScrollIndicator={false}
              // 초기 렌더링할 페이지 수 (필요에 따라 조정)
              initialNumToRender={isSearching ? searchPages.length : pages.length}
            />
          )}
        </View>

        {/* "더 보기" 안내 텍스트 */}
        <Text style={styles.moreText}>쓸어내려 더 보기</Text>
      </View>
    </SafeAreaView>
  );
};

export default ProductScreen;