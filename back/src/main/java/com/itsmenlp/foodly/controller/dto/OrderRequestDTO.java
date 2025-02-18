package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderRequestDTO {

    @NotNull(message = "Payment ID is required")
    private Long paymentId;

    @NotNull(message = "Address ID is required")
    private Long addressId;

    @NotBlank(message = "Order status is required")
    private String orderStatus;

    @NotNull(message = "Total amount is required")
    @Positive(message = "Total amount must be positive")
    private Integer totalAmount;

    @NotNull(message = "Order items are required")
    private List<OrderItemRequestDTO> orderItems;
}