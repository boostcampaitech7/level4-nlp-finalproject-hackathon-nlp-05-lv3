package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemServiceRequestDTO {

    private Long productId;
    private Integer quantity;
    private Integer unitPrice;
}