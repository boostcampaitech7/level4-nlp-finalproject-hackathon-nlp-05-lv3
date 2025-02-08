package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Product;
import com.itsmenlp.foodly.entity.Review;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.ProductRepository;
import com.itsmenlp.foodly.repository.ReviewRepository;
import com.itsmenlp.foodly.service.dto.ReviewServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.ReviewServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ReviewServiceImpl implements ReviewService {

    private final ReviewRepository reviewRepository;
    private final ProductRepository productRepository;

    @Override
    @Transactional
    public ReviewServiceResponseDTO createReview(Long productId, ReviewServiceRequestDTO requestDTO) {
        Product product = getProductById(productId);

        Review review = Review.builder()
                .product(product)
                .rate(requestDTO.getRate())
                .comment(requestDTO.getComment())
                .build();

        Review savedReview = reviewRepository.save(review);

        return mapToServiceResponseDTO(savedReview);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ReviewServiceResponseDTO> getAllReviews(Long productId) {
        Product product = getProductById(productId);
        List<Review> reviews = reviewRepository.findByProduct(product);

        return reviews.stream()
                .map(this::mapToServiceResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public ReviewServiceResponseDTO getReviewById(Long productId, Long reviewId) {
        Product product = getProductById(productId);
        Review review = getReviewByIdAndProduct(reviewId, product);

        return mapToServiceResponseDTO(review);
    }

    @Override
    @Transactional
    public ReviewServiceResponseDTO updateReview(Long productId, Long reviewId, ReviewServiceRequestDTO requestDTO) {
        Product product = getProductById(productId);
        Review review = getReviewByIdAndProduct(reviewId, product);

        review.setRate(requestDTO.getRate());
        review.setComment(requestDTO.getComment());

        Review updatedReview = reviewRepository.save(review);

        return mapToServiceResponseDTO(updatedReview);
    }

    @Override
    @Transactional
    public void deleteReview(Long productId, Long reviewId) {
        Product product = getProductById(productId);
        Review review = getReviewByIdAndProduct(reviewId, product);

        reviewRepository.delete(review);
    }

    private Product getProductById(Long productId) {
        return productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + productId));
    }

    private Review getReviewByIdAndProduct(Long reviewId, Product product) {
        return reviewRepository.findById(reviewId)
                .filter(review -> review.getProduct().equals(product))
                .orElseThrow(() -> new ResourceNotFoundException("Review not found with id: " + reviewId + " for product id: " + product.getProductId()));
    }

    private ReviewServiceResponseDTO mapToServiceResponseDTO(Review review) {
        return ReviewServiceResponseDTO.builder()
                .reviewId(review.getReviewId())
                .productId(review.getProduct().getProductId())
                .rate(review.getRate())
                .comment(review.getComment())
                .createdAt(review.getCreatedAt())
                .updatedAt(review.getUpdatedAt())
                .build();
    }
}