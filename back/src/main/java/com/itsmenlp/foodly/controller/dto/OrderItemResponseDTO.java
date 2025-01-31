package com.itsmenlp.foodly.controller.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemResponseDTO {

    private Long orderItemId;
    private Long productId;
    private String productName;
    private Integer quantity;
    private Integer unitPrice;
}