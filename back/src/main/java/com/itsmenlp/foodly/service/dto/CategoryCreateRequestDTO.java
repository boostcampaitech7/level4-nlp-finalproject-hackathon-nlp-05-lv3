package com.itsmenlp.foodly.service.dto;

import lombok.*;

import jakarta.validation.constraints.NotBlank;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryCreateRequestDTO {

    @NotBlank(message = "카테고리 이름은 필수입니다.")
    private String name;
}