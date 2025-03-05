package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Description;
import com.itsmenlp.foodly.entity.Product;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.DescriptionRepository;
import com.itsmenlp.foodly.repository.ProductRepository;
import com.itsmenlp.foodly.service.dto.DescriptionServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.DescriptionServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class DescriptionServiceImpl implements DescriptionService {

    private final DescriptionRepository descriptionRepository;
    private final ProductRepository productRepository;

    @Override
    @Transactional
    public DescriptionServiceResponseDTO createDescription(Long productId, DescriptionServiceRequestDTO requestDTO) {
        // 상품 존재 여부 확인
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + productId));

        // Description이 이미 존재하는지 확인
        if (descriptionRepository.existsById(productId)) {
            throw new IllegalArgumentException("Description already exists for product id: " + productId);
        }

        // Description 엔티티 생성
        Description description = Description.builder()
                .product(product)
                .summaryExp(requestDTO.getSummaryExp())
                .summaryCook(requestDTO.getSummaryCook())
                .summaryStore(requestDTO.getSummaryStore())
                .cautionAllergy1(requestDTO.getCautionAllergy1())
                .cautionAllergy2(requestDTO.getCautionAllergy2())
                .cautionStore(requestDTO.getCautionStore())
                .sizeDescription(requestDTO.getSizeDescription())
                .sizeImageUrl(requestDTO.getSizeImageUrl())
                .ingredient(requestDTO.getIngredient())
                .nutrition(requestDTO.getNutrition())
                .reviewGoodTaste(requestDTO.getReviewGoodTaste())
                .reviewGoodTasteNum(requestDTO.getReviewGoodTasteNum())
                .reviewGoodDelivery(requestDTO.getReviewGoodDelivery())
                .reviewGoodDeliveryNum(requestDTO.getReviewGoodDeliveryNum())
                .reviewBadTaste(requestDTO.getReviewBadTaste())
                .reviewBadTasteNum(requestDTO.getReviewBadTasteNum())
                .reviewBadDelivery(requestDTO.getReviewBadDelivery())
                .reviewBadDeliveryNum(requestDTO.getReviewBadDeliveryNum())
                .build();

        Description savedDescription = descriptionRepository.save(description);

        return mapToServiceResponseDTO(savedDescription);
    }

    @Override
    @Transactional(readOnly = true)
    public DescriptionServiceResponseDTO getDescription(Long productId) {
        Description description = descriptionRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Description not found for product id: " + productId));
        return mapToServiceResponseDTO(description);
    }

    @Override
    @Transactional
    public DescriptionServiceResponseDTO updateDescription(Long productId, DescriptionServiceRequestDTO requestDTO) {
        Description description = descriptionRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Description not found for product id: " + productId));

        description.setSummaryExp(requestDTO.getSummaryExp());
        description.setSummaryCook(requestDTO.getSummaryCook());
        description.setSummaryStore(requestDTO.getSummaryStore());
        description.setCautionAllergy1(requestDTO.getCautionAllergy1());
        description.setCautionAllergy2(requestDTO.getCautionAllergy2());
        description.setCautionStore(requestDTO.getCautionStore());
        description.setSizeDescription(requestDTO.getSizeDescription());
        description.setSizeImageUrl(requestDTO.getSizeImageUrl());
        description.setNutrition(requestDTO.getNutrition());
        description.setIngredient(requestDTO.getIngredient());
        description.setReviewGoodTaste(requestDTO.getReviewGoodTaste());
        description.setReviewGoodTasteNum(requestDTO.getReviewGoodTasteNum());
        description.setReviewGoodDelivery(requestDTO.getReviewGoodDelivery());
        description.setReviewGoodDeliveryNum(requestDTO.getReviewGoodDeliveryNum());
        description.setReviewBadTaste(requestDTO.getReviewBadTaste());
        description.setReviewBadTasteNum(requestDTO.getReviewBadTasteNum());
        description.setReviewBadDelivery(requestDTO.getReviewBadDelivery());
        description.setReviewBadDeliveryNum(requestDTO.getReviewBadDeliveryNum());

        Description updatedDescription = descriptionRepository.save(description);

        return mapToServiceResponseDTO(updatedDescription);
    }

    @Override
    @Transactional
    public void deleteDescription(Long productId) {
        Description description = descriptionRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Description not found for product id: " + productId));
        descriptionRepository.delete(description);
    }

    private DescriptionServiceResponseDTO mapToServiceResponseDTO(Description description) {
        return DescriptionServiceResponseDTO.builder()
                .productId(description.getProduct().getProductId())
                .summaryExp(description.getSummaryExp())
                .summaryCook(description.getSummaryCook())
                .summaryStore(description.getSummaryStore())
                .cautionAllergy1(description.getCautionAllergy1())
                .cautionAllergy2(description.getCautionAllergy2())
                .cautionStore(description.getCautionStore())
                .sizeDescription(description.getSizeDescription())
                .sizeImageUrl(description.getSizeImageUrl())
                .nutrition(description.getNutrition())
                .ingredient(description.getIngredient())
                .reviewGoodTaste(description.getReviewGoodTaste())
                .reviewGoodTasteNum(description.getReviewGoodTasteNum())
                .reviewGoodDelivery(description.getReviewGoodDelivery())
                .reviewGoodDeliveryNum(description.getReviewGoodDeliveryNum())
                .reviewBadTaste(description.getReviewBadTaste())
                .reviewBadTasteNum(description.getReviewBadTasteNum())
                .reviewBadDelivery(description.getReviewBadDelivery())
                .reviewBadDeliveryNum(description.getReviewBadDeliveryNum())
                .createdAt(description.getCreatedAt())
                .updatedAt(description.getUpdatedAt())
                .build();
    }
}