package com.itsmenlp.foodly.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "DESCRIPTIONS")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Description {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long descriptionId;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    private Product product;

    @Column
    private String summaryExp;

    @Column
    private String summaryCook;

    @Column
    private String summaryStore;

    @Column
    private String cautionAllergy1;

    @Column
    private String cautionAllergy2;

    @Column
    private String cautionStore;

    @Column
    private String sizeDescription;

    @Column
    private String sizeImageUrl;

    @Column
    private String ingredient;

    @Column
    private String nutrition;

    @Column
    private String reviewGoodTaste;

    @Column
    private Integer reviewGoodTasteNum;

    @Column
    private String reviewGoodDelivery;

    @Column
    private Integer reviewGoodDeliveryNum;

    @Column
    private String reviewBadTaste;

    @Column
    private Integer reviewBadTasteNum;

    @Column
    private String reviewBadDelivery;

    @Column
    private Integer reviewBadDeliveryNum;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}