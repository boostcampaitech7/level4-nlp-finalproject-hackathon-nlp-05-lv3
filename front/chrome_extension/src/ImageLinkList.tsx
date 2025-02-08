import React from 'react';

interface ImageLinkListProps {
  images: string[];
}

/**
 * ImageLinkList 컴포넌트
 * - images: 수집된 이미지 src 배열
 * - 각 src를 텍스트 링크 형태로 보여줍니다.
 */
const ImageLinkList: React.FC<ImageLinkListProps> = ({ images }) => {
  if (images.length === 0) {
    return <p>이미지가 없습니다.</p>;
  }

  return (
    <ul style={{ listStyle: 'none', padding: 0 }}>
      {images.map((src, index) => (
        <li key={index} style={{ marginBottom: '8px' }}>
          <a
            href={src}
            target="_blank"
            rel="noopener noreferrer"
            style={{ textDecoration: 'none', color: '#007bff' }}
          >
            {src}
          </a>
        </li>
      ))}
    </ul>
  );
};

export default ImageLinkList;