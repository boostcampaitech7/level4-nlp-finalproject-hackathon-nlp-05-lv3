package com.itsmenlp.foodly.controller.dto;

import lombok.*;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DescriptionResponseDTO {

    private Long productId;
    private String summaryExp;
    private String summaryCook;
    private String summaryStore;
    private String cautionAllergy1;
    private String cautionAllergy2;
    private String cautionStore;
    private String sizeDescription;
    private String sizeImageUrl;
    private String ingredient;
    private String nutrition;
    private String reviewGoodTaste;
    private Integer reviewGoodTasteNum;
    private String reviewGoodDelivery;
    private Integer reviewGoodDeliveryNum;
    private String reviewBadTaste;
    private Integer reviewBadTasteNum;
    private String reviewBadDelivery;
    private Integer reviewBadDeliveryNum;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}