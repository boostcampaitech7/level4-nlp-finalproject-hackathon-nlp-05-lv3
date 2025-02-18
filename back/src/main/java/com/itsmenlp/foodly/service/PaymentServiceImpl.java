package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Payment;
import com.itsmenlp.foodly.entity.User;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.PaymentRepository;
import com.itsmenlp.foodly.repository.UserRepository;
import com.itsmenlp.foodly.service.dto.PaymentServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.PaymentServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PaymentServiceImpl implements PaymentService {

    private final PaymentRepository paymentRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional
    public PaymentServiceResponseDTO createPayment(Long userId, PaymentServiceRequestDTO requestDTO) {
        User user = getUserById(userId);

        Payment payment = Payment.builder()
                .user(user)
                .status(requestDTO.getStatus())
                .paymentAmount(requestDTO.getPaymentAmount())
                .build();

        Payment savedPayment = paymentRepository.save(payment);

        return mapToServiceResponseDTO(savedPayment);
    }

    @Override
    @Transactional(readOnly = true)
    public List<PaymentServiceResponseDTO> getAllPayments(Long userId) {
        User user = getUserById(userId);
        List<Payment> payments = paymentRepository.findByUser(user);

        return payments.stream()
                .map(this::mapToServiceResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public PaymentServiceResponseDTO getPaymentById(Long userId, Long paymentId) {
        User user = getUserById(userId);
        Payment payment = getPaymentByIdAndUser(paymentId, user);

        return mapToServiceResponseDTO(payment);
    }

    @Override
    @Transactional
    public PaymentServiceResponseDTO updatePayment(Long userId, Long paymentId, PaymentServiceRequestDTO requestDTO) {
        User user = getUserById(userId);
        Payment payment = getPaymentByIdAndUser(paymentId, user);

        payment.setStatus(requestDTO.getStatus());
        payment.setPaymentAmount(requestDTO.getPaymentAmount());

        Payment updatedPayment = paymentRepository.save(payment);

        return mapToServiceResponseDTO(updatedPayment);
    }

    @Override
    @Transactional
    public void deletePayment(Long userId, Long paymentId) {
        User user = getUserById(userId);
        Payment payment = getPaymentByIdAndUser(paymentId, user);

        paymentRepository.delete(payment);
    }

    private User getUserById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
    }

    private Payment getPaymentByIdAndUser(Long paymentId, User user) {
        return paymentRepository.findById(paymentId)
                .filter(payment -> payment.getUser().equals(user))
                .orElseThrow(() -> new ResourceNotFoundException("Payment not found with id: " + paymentId + " for user id: " + user.getUserId()));
    }

    private PaymentServiceResponseDTO mapToServiceResponseDTO(Payment payment) {
        return PaymentServiceResponseDTO.builder()
                .paymentId(payment.getPaymentId())
                .userId(payment.getUser().getUserId())
                .status(payment.getStatus())
                .paymentAmount(payment.getPaymentAmount())
                .paymentDate(payment.getPaymentDate())
                .build();
    }
}