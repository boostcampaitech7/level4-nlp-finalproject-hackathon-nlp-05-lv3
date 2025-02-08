package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProductResponseDTO {
    private Long productId;
    private Long categoryId;
    private String name;
    private String thumbnailUrl;
    private String thumbnailCaption;
    private String mall;
    private Integer price;
    private Integer stock;
    private Float rating;
    private String coupon;
    private String delivery;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}