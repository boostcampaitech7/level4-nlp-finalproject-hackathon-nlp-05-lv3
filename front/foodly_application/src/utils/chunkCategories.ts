import { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { faQuestion } from "@fortawesome/free-solid-svg-icons";

// utils/chunkCategories.ts
export interface Category {
    id: string;
    name: string;
    icon: IconDefinition;
  }
  
  /**
   * categories 배열을 size(6)만큼 잘라 2차원 배열로 반환합니다.
   * 마지막 덩어리가 6개보다 작으면 빈 항목을 추가하여 6개로 맞춥니다.
   */
  export const chunkCategories = (categories: Category[], size: number): Category[][] => {
    const chunks: Category[][] = [];
    for (let i = 0; i < categories.length; i += size) {
      const chunk = categories.slice(i, i + size);
      while (chunk.length < size) {
        chunk.push({ id: `empty-${chunk.length}`, name: '', icon: faQuestion });
      }
      chunks.push(chunk);
    }
    return chunks;
  };