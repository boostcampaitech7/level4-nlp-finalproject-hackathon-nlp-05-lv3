package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AddressResponseDTO {

    private Long addressId;
    private Long userId;
    private String address;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}