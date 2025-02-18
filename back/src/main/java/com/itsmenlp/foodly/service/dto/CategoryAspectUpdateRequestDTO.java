package com.itsmenlp.foodly.service.dto;

import lombok.*;

import jakarta.validation.constraints.NotBlank;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryAspectUpdateRequestDTO {

    @NotBlank(message = "Aspect는 필수입니다.")
    private String aspect;
}