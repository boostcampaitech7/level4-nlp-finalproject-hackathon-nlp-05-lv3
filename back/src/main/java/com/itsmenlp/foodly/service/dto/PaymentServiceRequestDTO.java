package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PaymentServiceRequestDTO {

    private String status;
    private Integer paymentAmount;
}