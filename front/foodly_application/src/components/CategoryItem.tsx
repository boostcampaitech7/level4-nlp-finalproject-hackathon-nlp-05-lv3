// components/CategoryItem.tsx
import React from 'react';
import Config from 'react-native-config';
import axios from 'axios';
import { TouchableOpacity, Text, View, Alert } from 'react-native';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { categoryStyles } from '../styles/categoryStyles';

// 네비게이션 파라미터 타입 정의 (CategoryStack 내의 Product 스크린)
type CategoryStackParamList = {
  // Product 스크린으로 이동할 때 상품 목록과 카테고리명을 전달합니다.
  Product: { products: any; category: { id: string, name: string } };
};

type NavigationProp = StackNavigationProp<CategoryStackParamList, 'Product'>;

interface CategoryItemProps {
  id: string;
  name: string;
  icon: IconDefinition;
}

const CategoryItem: React.FC<CategoryItemProps> = ({ id, name, icon }) => {
  const navigation = useNavigation<NavigationProp>();

  if (!name) {
    return <View style={categoryStyles.emptyItem} />;
  }

  const handlePress = async () => {
    try {
      // 카테고리 ID를 포함하여 해당 카테고리의 상품 데이터를 요청합니다.
      const response = await axios.get(`${Config.BASE_URL}/api/product/categories/${id}`);
      
      // API로부터 받은 상품 목록 데이터
      const products = response.data;
      
      console.log('Fetched products for category', id, products);
      
      // ProductScreen으로 네비게이트하면서 상품 데이터와 카테고리 이름을 전달합니다.
      navigation.navigate('Product', { products, category: {id: id, name: name} });
    } catch (error) {
      console.error('Error fetching products for category', id, error);
      Alert.alert('Error', '상품 정보를 가져오는데 실패했습니다.');
    }
  };

  return (
    <TouchableOpacity style={categoryStyles.itemContainer} onPress={handlePress}>
      <FontAwesomeIcon icon={icon} size={32} style={categoryStyles.itemIcon} />
      <Text style={categoryStyles.name}>{name}</Text>
    </TouchableOpacity>
  );
};

export default CategoryItem;