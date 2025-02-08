package com.itsmenlp.foodly.service.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AddressServiceResponseDTO {

    private Long addressId;
    private Long userId;
    private String address;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}