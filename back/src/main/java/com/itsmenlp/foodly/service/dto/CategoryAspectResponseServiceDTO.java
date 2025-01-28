package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryAspectResponseServiceDTO {
    private Long id;
    private String aspect;
}