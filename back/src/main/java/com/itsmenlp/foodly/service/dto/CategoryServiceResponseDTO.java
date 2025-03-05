package com.itsmenlp.foodly.service.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CategoryServiceResponseDTO {
    private Long categoryId;
    private String name;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<CategoryAspectServiceResponseDTO> aspects;
}