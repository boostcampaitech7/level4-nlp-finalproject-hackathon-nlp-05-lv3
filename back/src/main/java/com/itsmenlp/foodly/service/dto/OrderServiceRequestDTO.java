package com.itsmenlp.foodly.service.dto;

import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderServiceRequestDTO {

    private Long paymentId;
    private Long addressId;
    private String orderStatus;
    private Integer totalAmount;
    private List<OrderItemServiceRequestDTO> orderItems;
}