package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.DescriptionRequestDTO;
import com.itsmenlp.foodly.controller.dto.DescriptionResponseDTO;
import com.itsmenlp.foodly.service.DescriptionService;
import com.itsmenlp.foodly.service.dto.DescriptionRequestServiceDTO;
import com.itsmenlp.foodly.service.dto.DescriptionResponseServiceDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/descriptions")
@RequiredArgsConstructor
public class DescriptionController {

    private final DescriptionService descriptionService;

    /**
     * 상품 설명 생성
     * POST /api/descriptions/{productId}
     */
    @PostMapping("/{productId}")
    public ResponseEntity<DescriptionResponseDTO> createDescription(
            @PathVariable Long productId,
            @RequestBody DescriptionRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        DescriptionRequestServiceDTO serviceRequestDTO = DescriptionRequestServiceDTO.builder()
                .summaryExp(requestDTO.getSummaryExp())
                .summaryCook(requestDTO.getSummaryCook())
                .summaryStore(requestDTO.getSummaryStore())
                .cautionAllergy1(requestDTO.getCautionAllergy1())
                .cautionAllergy2(requestDTO.getCautionAllergy2())
                .cautionStore(requestDTO.getCautionStore())
                .sizeDescription(requestDTO.getSizeDescription())
                .sizeImageUrl(requestDTO.getSizeImageUrl())
                .nutrition(requestDTO.getNutrition())
                .ingredient(requestDTO.getIngredient())
                .reviewGoodTaste(requestDTO.getReviewGoodTaste())
                .reviewGoodTasteNum(requestDTO.getReviewGoodTasteNum())
                .reviewGoodDelivery(requestDTO.getReviewGoodDelivery())
                .reviewGoodDeliveryNum(requestDTO.getReviewGoodDeliveryNum())
                .reviewBadTaste(requestDTO.getReviewBadTaste())
                .reviewBadTasteNum(requestDTO.getReviewBadTasteNum())
                .reviewBadDelivery(requestDTO.getReviewBadDelivery())
                .reviewBadDeliveryNum(requestDTO.getReviewBadDeliveryNum())
                .build();

        DescriptionResponseServiceDTO serviceResponseDTO = descriptionService.createDescription(productId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        DescriptionResponseDTO responseDTO = DescriptionResponseDTO.builder()
                .productId(serviceResponseDTO.getProductId())
                .summaryExp(serviceResponseDTO.getSummaryExp())
                .summaryCook(serviceResponseDTO.getSummaryCook())
                .summaryStore(serviceResponseDTO.getSummaryStore())
                .cautionAllergy1(serviceResponseDTO.getCautionAllergy1())
                .cautionAllergy2(serviceResponseDTO.getCautionAllergy2())
                .cautionStore(serviceResponseDTO.getCautionStore())
                .sizeDescription(serviceResponseDTO.getSizeDescription())
                .sizeImageUrl(serviceResponseDTO.getSizeImageUrl())
                .nutrition(serviceResponseDTO.getNutrition())
                .ingredient(serviceResponseDTO.getIngredient())
                .reviewGoodTaste(serviceResponseDTO.getReviewGoodTaste())
                .reviewGoodTasteNum(serviceResponseDTO.getReviewGoodTasteNum())
                .reviewGoodDelivery(serviceResponseDTO.getReviewGoodDelivery())
                .reviewGoodDeliveryNum(serviceResponseDTO.getReviewGoodDeliveryNum())
                .reviewBadTaste(serviceResponseDTO.getReviewBadTaste())
                .reviewBadTasteNum(serviceResponseDTO.getReviewBadTasteNum())
                .reviewBadDelivery(serviceResponseDTO.getReviewBadDelivery())
                .reviewBadDeliveryNum(serviceResponseDTO.getReviewBadDeliveryNum())
                .createdAt(serviceResponseDTO.getCreatedAt())
                .updatedAt(serviceResponseDTO.getUpdatedAt())
                .build();

        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    /**
     * 상품 설명 조회
     * GET /api/descriptions/{productId}
     */
    @GetMapping("/{productId}")
    public ResponseEntity<DescriptionResponseDTO> getDescription(@PathVariable Long productId) {
        DescriptionResponseServiceDTO serviceResponseDTO = descriptionService.getDescription(productId);

        // Service DTO를 Controller DTO로 변환
        return getDescriptionResponseDTOResponseEntity(serviceResponseDTO);
    }

    /**
     * 상품 설명 업데이트
     * PUT /api/descriptions/{productId}
     */
    @PutMapping("/{productId}")
    public ResponseEntity<DescriptionResponseDTO> updateDescription(
            @PathVariable Long productId,
            @RequestBody DescriptionRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        DescriptionRequestServiceDTO serviceRequestDTO = DescriptionRequestServiceDTO.builder()
                .summaryExp(requestDTO.getSummaryExp())
                .summaryCook(requestDTO.getSummaryCook())
                .summaryStore(requestDTO.getSummaryStore())
                .cautionAllergy1(requestDTO.getCautionAllergy1())
                .cautionAllergy2(requestDTO.getCautionAllergy2())
                .cautionStore(requestDTO.getCautionStore())
                .sizeDescription(requestDTO.getSizeDescription())
                .sizeImageUrl(requestDTO.getSizeImageUrl())
                .nutrition(requestDTO.getNutrition())
                .ingredient(requestDTO.getIngredient())
                .reviewGoodTaste(requestDTO.getReviewGoodTaste())
                .reviewGoodTasteNum(requestDTO.getReviewGoodTasteNum())
                .reviewGoodDelivery(requestDTO.getReviewGoodDelivery())
                .reviewGoodDeliveryNum(requestDTO.getReviewGoodDeliveryNum())
                .reviewBadTaste(requestDTO.getReviewBadTaste())
                .reviewBadTasteNum(requestDTO.getReviewBadTasteNum())
                .reviewBadDelivery(requestDTO.getReviewBadDelivery())
                .reviewBadDeliveryNum(requestDTO.getReviewBadDeliveryNum())
                .build();

        DescriptionResponseServiceDTO serviceResponseDTO = descriptionService.updateDescription(productId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        return getDescriptionResponseDTOResponseEntity(serviceResponseDTO);
    }

    /**
     * 상품 설명 삭제
     * DELETE /api/descriptions/{productId}
     */
    @DeleteMapping("/{productId}")
    public ResponseEntity<Void> deleteDescription(@PathVariable Long productId) {
        descriptionService.deleteDescription(productId);
        return ResponseEntity.noContent().build();
    }

    private ResponseEntity<DescriptionResponseDTO> getDescriptionResponseDTOResponseEntity(DescriptionResponseServiceDTO serviceResponseDTO) {
        DescriptionResponseDTO responseDTO = DescriptionResponseDTO.builder()
                .productId(serviceResponseDTO.getProductId())
                .summaryExp(serviceResponseDTO.getSummaryExp())
                .summaryCook(serviceResponseDTO.getSummaryCook())
                .summaryStore(serviceResponseDTO.getSummaryStore())
                .cautionAllergy1(serviceResponseDTO.getCautionAllergy1())
                .cautionAllergy2(serviceResponseDTO.getCautionAllergy2())
                .cautionStore(serviceResponseDTO.getCautionStore())
                .sizeDescription(serviceResponseDTO.getSizeDescription())
                .sizeImageUrl(serviceResponseDTO.getSizeImageUrl())
                .nutrition(serviceResponseDTO.getNutrition())
                .ingredient(serviceResponseDTO.getIngredient())
                .reviewGoodTaste(serviceResponseDTO.getReviewGoodTaste())
                .reviewGoodTasteNum(serviceResponseDTO.getReviewGoodTasteNum())
                .reviewGoodDelivery(serviceResponseDTO.getReviewGoodDelivery())
                .reviewGoodDeliveryNum(serviceResponseDTO.getReviewGoodDeliveryNum())
                .reviewBadTaste(serviceResponseDTO.getReviewBadTaste())
                .reviewBadTasteNum(serviceResponseDTO.getReviewBadTasteNum())
                .reviewBadDelivery(serviceResponseDTO.getReviewBadDelivery())
                .reviewBadDeliveryNum(serviceResponseDTO.getReviewBadDeliveryNum())
                .createdAt(serviceResponseDTO.getCreatedAt())
                .updatedAt(serviceResponseDTO.getUpdatedAt())
                .build();

        return ResponseEntity.ok(responseDTO);
    }
}