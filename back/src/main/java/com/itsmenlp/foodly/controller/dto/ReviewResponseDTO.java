package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewResponseDTO {

    private Long reviewId;
    private Long productId;
    private Integer rate;
    private String comment;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}