package com.itsmenlp.foodly.controller.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryAspectResponseDTO {
    private Long id;
    private String aspect;
}