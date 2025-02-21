package com.itsmenlp.foodly.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductRankId implements Serializable {
    private Integer productRankId;
    private Integer productId;
    private Integer aspectId;
    private Integer categoryId;
}