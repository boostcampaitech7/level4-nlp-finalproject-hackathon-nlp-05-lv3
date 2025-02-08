package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CartServiceRequestDTO {

    private Long productId;
    private Integer quantity;
}