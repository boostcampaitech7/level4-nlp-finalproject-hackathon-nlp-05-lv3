package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemServiceResponseDTO {

    private Long orderItemId;
    private Long productId;
    private String productName;
    private Integer quantity;
    private Integer unitPrice;
}