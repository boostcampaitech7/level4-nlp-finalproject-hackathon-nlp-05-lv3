package com.itsmenlp.foodly.service.dto;

import lombok.*;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProductUpdateRequestDTO {

    @NotNull(message = "카테고리 ID는 필수입니다.")
    private Long categoryId;

    @NotBlank(message = "상품 이름은 필수입니다.")
    private String name;

    private String thumbnailUrl;
    private String thumbnailCaption;
    private String thumbnailCaptionShort;
    private String mall;

    @Min(value = 0, message = "가격은 0 이상이어야 합니다.")
    private Integer price;

    @Min(value = 0, message = "재고는 0 이상이어야 합니다.")
    private Integer stock;

    @Min(value = 0, message = "평점은 0 이상이어야 합니다.")
    private Float rating;

    private String coupon;
    private String delivery;
}