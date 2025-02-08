package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import jakarta.validation.constraints.NotBlank;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryAspectRequestDTO {

    @NotBlank(message = "Aspect는 필수입니다.")
    private String aspect;
}