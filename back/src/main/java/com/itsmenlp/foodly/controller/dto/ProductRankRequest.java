package com.itsmenlp.foodly.controller.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductRankRequest {
    private Integer productRankId;
    private Integer productId;
    private Integer aspectId;
    private Integer categoryId;
    private Integer productRank;
}