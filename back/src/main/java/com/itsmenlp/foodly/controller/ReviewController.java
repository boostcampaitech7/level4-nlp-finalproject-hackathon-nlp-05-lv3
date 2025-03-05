package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.ReviewRequestDTO;
import com.itsmenlp.foodly.controller.dto.ReviewResponseDTO;
import com.itsmenlp.foodly.service.ReviewService;
import com.itsmenlp.foodly.service.dto.ReviewServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.ReviewServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/product/{productId}/review")
@RequiredArgsConstructor
public class ReviewController {

    private final ReviewService reviewService;

    /**
     * 리뷰 생성
     * POST /api/products/{productId}/review
     */
    @PostMapping
    public ResponseEntity<ReviewResponseDTO> createReview(
            @PathVariable Long productId,
            @Valid @RequestBody ReviewRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        ReviewServiceRequestDTO serviceRequestDTO = ReviewServiceRequestDTO.builder()
                .rate(requestDTO.getRate())
                .comment(requestDTO.getComment())
                .build();

        ReviewServiceResponseDTO serviceResponseDTO = reviewService.createReview(productId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        ReviewResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    /**
     * 모든 리뷰 조회
     * GET /api/products/{productId}/review
     */
    @GetMapping
    public ResponseEntity<List<ReviewResponseDTO>> getAllReviews(@PathVariable Long productId) {
        List<ReviewServiceResponseDTO> serviceResponseDTOs = reviewService.getAllReviews(productId);

        // Service DTO를 Controller DTO로 변환
        List<ReviewResponseDTO> responseDTOs = serviceResponseDTOs.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responseDTOs);
    }

    /**
     * 특정 리뷰 조회
     * GET /api/products/{productId}/reviews/{reviewId}
     */
    @GetMapping("/{reviewId}")
    public ResponseEntity<ReviewResponseDTO> getReviewById(
            @PathVariable Long productId,
            @PathVariable Long reviewId) {

        ReviewServiceResponseDTO serviceResponseDTO = reviewService.getReviewById(productId, reviewId);

        // Service DTO를 Controller DTO로 변환
        ReviewResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 리뷰 업데이트
     * PUT /api/products/{productId}/reviews/{reviewId}
     */
    @PutMapping("/{reviewId}")
    public ResponseEntity<ReviewResponseDTO> updateReview(
            @PathVariable Long productId,
            @PathVariable Long reviewId,
            @Valid @RequestBody ReviewRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        ReviewServiceRequestDTO serviceRequestDTO = ReviewServiceRequestDTO.builder()
                .rate(requestDTO.getRate())
                .comment(requestDTO.getComment())
                .build();

        ReviewServiceResponseDTO serviceResponseDTO = reviewService.updateReview(productId, reviewId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        ReviewResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 리뷰 삭제
     * DELETE /api/products/{productId}/reviews/{reviewId}
     */
    @DeleteMapping("/{reviewId}")
    public ResponseEntity<Void> deleteReview(
            @PathVariable Long productId,
            @PathVariable Long reviewId) {

        reviewService.deleteReview(productId, reviewId);
        return ResponseEntity.noContent().build();
    }

    private ReviewResponseDTO mapToResponseDTO(ReviewServiceResponseDTO serviceResponseDTO) {
        return ReviewResponseDTO.builder()
                .reviewId(serviceResponseDTO.getReviewId())
                .productId(serviceResponseDTO.getProductId())
                .rate(serviceResponseDTO.getRate())
                .comment(serviceResponseDTO.getComment())
                .createdAt(serviceResponseDTO.getCreatedAt())
                .updatedAt(serviceResponseDTO.getUpdatedAt())
                .build();
    }
}