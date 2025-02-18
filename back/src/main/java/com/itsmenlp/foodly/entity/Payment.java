package com.itsmenlp.foodly.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "PAYMENTS")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Payment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long paymentId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String status;

    @Column(nullable = false)
    private Integer paymentAmount;

    @Column(nullable = false, updatable = false)
    private LocalDateTime paymentDate;

    @PrePersist
    protected void onCreate() {
        this.paymentDate = LocalDateTime.now();
    }
}