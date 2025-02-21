package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PaymentResponseDTO {

    private Long paymentId;
    private Long userId;
    private String status;
    private Integer paymentAmount;
    private LocalDateTime paymentDate;
}