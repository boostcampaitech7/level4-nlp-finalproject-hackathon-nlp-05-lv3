package com.itsmenlp.foodly.service.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PaymentServiceResponseDTO {

    private Long paymentId;
    private Long userId;
    private String status;
    private Integer paymentAmount;
    private LocalDateTime paymentDate;
}