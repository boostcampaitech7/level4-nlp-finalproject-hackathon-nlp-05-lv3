package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.PaymentServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.PaymentServiceResponseDTO;

import java.util.List;

public interface PaymentService {

    PaymentServiceResponseDTO createPayment(Long userId, PaymentServiceRequestDTO requestDTO);
    List<PaymentServiceResponseDTO> getAllPayments(Long userId);
    PaymentServiceResponseDTO getPaymentById(Long userId, Long paymentId);
    PaymentServiceResponseDTO updatePayment(Long userId, Long paymentId, PaymentServiceRequestDTO requestDTO);
    void deletePayment(Long userId, Long paymentId);
}