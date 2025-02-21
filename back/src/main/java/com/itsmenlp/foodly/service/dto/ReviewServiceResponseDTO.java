package com.itsmenlp.foodly.service.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewServiceResponseDTO {

    private Long reviewId;
    private Long productId;
    private Integer rate;
    private String comment;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}