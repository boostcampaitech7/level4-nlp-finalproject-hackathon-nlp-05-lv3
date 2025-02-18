package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryResponseDTO {
    private Long categoryId;
    private String name;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<CategoryAspectResponseDTO> aspects;
}