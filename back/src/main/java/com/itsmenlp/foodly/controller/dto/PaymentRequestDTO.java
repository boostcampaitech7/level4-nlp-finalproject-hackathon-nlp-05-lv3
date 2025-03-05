package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PaymentRequestDTO {

    @NotBlank(message = "Status is required")
    private String status;

    @NotNull(message = "Payment amount is required")
    @Min(value = 1, message = "Payment amount must be at least 1")
    private Integer paymentAmount;
}