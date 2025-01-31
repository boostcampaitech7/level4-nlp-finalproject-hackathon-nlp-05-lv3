package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.ProductRank;
import com.itsmenlp.foodly.entity.ProductRankId;
import com.itsmenlp.foodly.repository.ProductRankRepository;
import com.itsmenlp.foodly.service.dto.ProductRankRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductRankResponseDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ProductRankService {

    @Autowired
    private ProductRankRepository productRankRepository;

    // 엔티티 -> DTO 변환
    private ProductRankResponseDTO convertToDto(ProductRank productRank) {
        return new ProductRankResponseDTO(
                productRank.getProductRankId(),
                productRank.getProductId(),
                productRank.getAspectId(),
                productRank.getCategoryId(),
                productRank.getProductRank()
        );
    }

    // 등록 (Create)
    public ProductRankResponseDTO createProductRank(ProductRankRequestDTO requestDto) {
        ProductRank productRank = new ProductRank(
                requestDto.getProductRankId(),
                requestDto.getProductId(),
                requestDto.getAspectId(),
                requestDto.getCategoryId(),
                requestDto.getProductRank()
        );
        ProductRank saved = productRankRepository.save(productRank);
        return convertToDto(saved);
    }

    // 단건 조회 (Read)
    public ProductRankResponseDTO getProductRank(Integer productRankId, Integer productId, Integer aspectId, Integer categoryId) {
        ProductRankId id = new ProductRankId(productRankId, productId, aspectId, categoryId);
        ProductRank productRank = productRankRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("ProductRank not found"));
        return convertToDto(productRank);
    }

    // 수정 (Update)
    public ProductRankResponseDTO updateProductRank(Integer productRankId, Integer productId, Integer aspectId, Integer categoryId, ProductRankRequestDTO requestDto) {
        ProductRankId id = new ProductRankId(productRankId, productId, aspectId, categoryId);
        ProductRank productRank = productRankRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("ProductRank not found"));
        productRank.setProductRank(requestDto.getProductRank());
        ProductRank updated = productRankRepository.save(productRank);
        return convertToDto(updated);
    }

    // 삭제 (Delete)
    public void deleteProductRank(Integer productRankId, Integer productId, Integer aspectId, Integer categoryId) {
        ProductRankId id = new ProductRankId(productRankId, productId, aspectId, categoryId);
        productRankRepository.deleteById(id);
    }

    // 전체 목록 조회
    public List<ProductRankResponseDTO> getAllProductRanks() {
        return productRankRepository.findAll()
                .stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    // 특정 aspect_id의 데이터를 rank(=COUNT) 내림차순 정렬하여 조회
    public List<ProductRankResponseDTO> getProductRanksByAspect(Integer aspectId) {
        List<ProductRank> list = productRankRepository.findByAspectIdOrderByProductRankDesc(aspectId);
        return list.stream().map(this::convertToDto).collect(Collectors.toList());
    }
}