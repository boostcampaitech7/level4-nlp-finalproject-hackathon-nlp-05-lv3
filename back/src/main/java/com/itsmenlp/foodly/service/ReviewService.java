package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.ReviewServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.ReviewServiceResponseDTO;

import java.util.List;

public interface ReviewService {

    ReviewServiceResponseDTO createReview(Long productId, ReviewServiceRequestDTO requestDTO);
    List<ReviewServiceResponseDTO> getAllReviews(Long productId);
    ReviewServiceResponseDTO getReviewById(Long productId, Long reviewId);
    ReviewServiceResponseDTO updateReview(Long productId, Long reviewId, ReviewServiceRequestDTO requestDTO);
    void deleteReview(Long productId, Long reviewId);
}