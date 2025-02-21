package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CartResponseDTO {

    private Long cartId;
    private Long userId;
    private Long productId;
    private String productName;
    private Integer quantity;
    private LocalDateTime addedAt;
}