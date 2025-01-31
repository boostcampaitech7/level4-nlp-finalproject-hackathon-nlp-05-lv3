package com.itsmenlp.foodly.service.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderServiceResponseDTO {

    private Long orderId;
    private Long userId;
    private Long paymentId;
    private Long addressId;
    private String orderStatus;
    private Integer totalAmount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<OrderItemServiceResponseDTO> orderItems;
}