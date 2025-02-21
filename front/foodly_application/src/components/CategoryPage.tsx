// components/CategoryPage.tsx
import React from 'react';
import { Text, View, StyleSheet, StyleProp, ViewStyle } from 'react-native';
import CategoryItem from './CategoryItem';
import { Category } from '../utils/chunkCategories';

import styles from '../styles/styles';
import { categoryStyles } from '../styles/categoryStyles';

interface PageProps {
  pageData: Category[];
  sizeInfo: { width: number; height: number };
}

const CategoryPage: React.FC<PageProps> = ({ pageData, sizeInfo }) => {
  const flattenedContainerStyle: StyleProp<ViewStyle> = StyleSheet.flatten(styles.container);
  const containerPaddingTop = (flattenedContainerStyle as any).paddingTop !== undefined
    ? (flattenedContainerStyle as any).paddingTop
    : (flattenedContainerStyle as any).padding || 0;
  const containerPaddingBottom = (flattenedContainerStyle as any).paddingBottom !== undefined
    ? (flattenedContainerStyle as any).paddingBottom
    : (flattenedContainerStyle as any).padding || 0;

  const containerPaddingVertical = containerPaddingTop + containerPaddingBottom;

  // 사용 가능한 전체 높이에서 패딩을 뺀 값을 3등분하여 각 행의 높이를 계산합니다.
  const availableHeight = sizeInfo.height - containerPaddingVertical;
  const rowHeight = availableHeight / 3;

  const rows = [];
  for (let i = 0; i < 3; i++) {
    // 예시로 한 행에 2개의 아이템을 넣는 구조라면
    const rowItems = pageData.slice(i * 2, i * 2 + 2);
    rows.push(
      <View
        key={`row-${i}`}
        style={[
          categoryStyles.rowContainer,
          { height: rowHeight } // 각 행의 높이를 동적으로 지정
        ]}
      >
        {rowItems.map(category => (
          <CategoryItem
            key={category.id}
            id={category.id}
            name={category.name}
            icon={category.icon}
          />
        ))}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {rows}
    </View>
  );
};

export default CategoryPage;