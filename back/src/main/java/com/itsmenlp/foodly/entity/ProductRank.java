package com.itsmenlp.foodly.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.persistence.*;

@Entity
@Table(name = "PRODUCTRANK")
@IdClass(ProductRankId.class)
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductRank {

    @Id
    @Column
    private Integer productRankId;

    @Id
    @Column
    private Integer productId;

    @Id
    @Column
    private Integer aspectId;

    @Id
    @Column
    private Integer categoryId;

    @Column
    private Integer productRank;
}