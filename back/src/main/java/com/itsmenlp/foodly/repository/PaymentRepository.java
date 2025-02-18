package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.Payment;
import com.itsmenlp.foodly.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PaymentRepository extends JpaRepository<Payment, Long> {

    List<Payment> findByUser(User user);
    boolean existsByPaymentIdAndUser(Long paymentId, User user);
}