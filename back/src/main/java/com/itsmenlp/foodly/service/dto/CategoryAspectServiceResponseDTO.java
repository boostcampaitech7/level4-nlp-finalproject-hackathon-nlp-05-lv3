package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryAspectServiceResponseDTO {
    private Long id;
    private String aspect;
}