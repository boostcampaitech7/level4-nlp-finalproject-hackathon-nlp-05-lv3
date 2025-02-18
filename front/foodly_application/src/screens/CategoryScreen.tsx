// screens/CategoryScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  Text,
  View,
  TextInput,
  FlatList,
  LayoutChangeEvent,
  TouchableOpacity
} from 'react-native';
import axios from 'axios';
import Config from 'react-native-config';
import CategoryPage from '../components/CategoryPage';
import { chunkCategories, Category } from '../utils/chunkCategories'; 
// 만약 제품용 chunk 함수가 별도로 필요하다면 chunkProducts라는 함수를 utils에 따로 만들 수도 있습니다.

import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { getIconForCategory } from '../components/CategoryIcon';

import styles from '../styles/styles';

// ▼ 새로 추가 (ProductPage import)
import ProductPage from '../components/ProductPage';

const CategoryScreen: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [flatListSize, setFlatListSize] = useState({ width: 0, height: 0 });

  // 검색어 상태
  const [searchTerm, setSearchTerm] = useState('');
  // 검색 결과 상태 (상품 리스트라 가정)
  const [searchResults, setSearchResults] = useState<any[]>([]);
  // 검색 모드 여부
  const [isSearching, setIsSearching] = useState(false);

  // 컴포넌트가 마운트될 때 백엔드에서 카테고리 데이터를 받아옴
  useEffect(() => {
    axios
      .get(`${Config.BASE_URL}/api/category`)
      .then(response => {
        // response.data는 CategoryResponseDTO 배열이라고 가정
        const fetchedCategories: Category[] = response.data.map((cat: any) => ({
          id: cat.categoryId.toString(), // id를 string으로 변환 (필요에 따라)
          name: cat.name,
          icon: getIconForCategory(cat.name),
        }));
        setCategories(fetchedCategories);
      })
      .catch(error => {
        console.error('Error fetching categories:', error);
      });
  }, []);

  // "검색" 아이콘을 눌렀을 때 호출되는 함수
  const handleSearch = () => {
    // 검색어가 없으면 검색을 수행하지 않고 리턴
    if (!searchTerm.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }

    setIsSearching(true);

    axios
      .get(`${Config.BASE_URL}/api/product/search`, {
        // 백엔드 API의 파라미터 이름이 예: `name`이라고 가정
        params: { name: searchTerm },
      })
      .then(response => {
        console.log('Search results:', response.data);
        setSearchResults(response.data); // 검색 결과를 상태에 저장
      })
      .catch(error => {
        console.error('Error searching products:', error);
      });
  };

  // 카테고리 배열을 chunkCategories 함수를 이용하여 페이지 단위로 분할
  const pages = chunkCategories(categories, 6);

  // ▼ 검색 결과도 3개씩 끊어서 ProductPage에서 표시 (상품이 3개 단위라고 가정)
  //   만약 ProductPage가 3개가 아니라 다른 개수를 처리한다면 해당 수치 조정
  const chunkSearchResults = (data: any[], size: number) => {
    const result = [];
    for (let i = 0; i < data.length; i += size) {
      result.push(data.slice(i, i + size));
    }
    return result;
  };

  const searchPages = chunkSearchResults(searchResults, 3);

  // FlatList 영역의 크기를 측정하는 콜백 함수
  const handleLayout = (event: LayoutChangeEvent) => {
    const { width, height } = event.nativeEvent.layout;
    setFlatListSize({ width, height });
  };

  return (
    <View style={styles.container}>
      {/* 검색창 */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="궁금한 상품을 검색해보세요"
          value={searchTerm}
          onChangeText={setSearchTerm}
          onSubmitEditing={handleSearch} // 엔터(Submit) 시 검색
        />
        {/* TouchableOpacity로 아이콘을 감싸 클릭 이벤트 처리 */}
        <TouchableOpacity onPress={handleSearch}>
          <FontAwesomeIcon
            icon={faMagnifyingGlass}
            style={styles.searchIcon}
          />
        </TouchableOpacity>
      </View>

      {/* 
        검색 중(isSearching=true)이라면 검색 결과를 표시,
        아니라면 기존 카테고리 페이지를 표시 
      */}
      {isSearching ? (
        // ▼ ProductPage 기반으로 검색결과를 표시
        <FlatList
          data={searchPages}
          keyExtractor={(_, index) => `search-page-${index}`}
          renderItem={({ item }) => (
            <ProductPage
              pageData={item} 
              screenLength={flatListSize.height} 
            />
          )}
          // 검색 결과 전체를 세로 스크롤로 보여주고 싶다면
          // pagingEnabled={false} 로 두고, decelerationRate="fast"도 제거/취향대로 설정
          pagingEnabled
          decelerationRate="fast"
          style={{ flex: 1, marginVertical: 12}}
          onLayout={handleLayout}
        />
      ) : (
        <>
          {/* 페이지 단위 스와이프(스크롤) 영역 */}
          <FlatList
            data={pages}
            keyExtractor={(_, index) => `page-${index}`}
            renderItem={({ item }) => (
              <CategoryPage pageData={item} sizeInfo={flatListSize} />
            )}
            pagingEnabled
            decelerationRate="fast"
            showsVerticalScrollIndicator={false}
            style={{ flex: 1 }}
            onLayout={handleLayout}
          />

          {/* "더 보기" 안내 텍스트 */}
          <Text style={styles.moreText}>쓸어내려 더 보기</Text>
        </>
      )}
    </View>
  );
};

export default CategoryScreen;