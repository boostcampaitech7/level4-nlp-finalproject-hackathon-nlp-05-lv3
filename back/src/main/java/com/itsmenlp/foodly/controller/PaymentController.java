package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.PaymentRequestDTO;
import com.itsmenlp.foodly.controller.dto.PaymentResponseDTO;
import com.itsmenlp.foodly.service.PaymentService;
import com.itsmenlp.foodly.service.dto.PaymentServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.PaymentServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user/{userId}/payment")
@RequiredArgsConstructor
public class PaymentController {

    private final PaymentService paymentService;

    /**
     * 결제 정보 생성
     * POST /api/user/{userId}/payment
     */
    @PostMapping
    public ResponseEntity<PaymentResponseDTO> createPayment(
            @PathVariable Long userId,
            @Valid @RequestBody PaymentRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        PaymentServiceRequestDTO serviceRequestDTO = PaymentServiceRequestDTO.builder()
                .status(requestDTO.getStatus())
                .paymentAmount(requestDTO.getPaymentAmount())
                .build();

        PaymentServiceResponseDTO serviceResponseDTO = paymentService.createPayment(userId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        PaymentResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    /**
     * 모든 결제 정보 조회
     * GET /api/user/{userId}/payment
     */
    @GetMapping
    public ResponseEntity<List<PaymentResponseDTO>> getAllPayments(@PathVariable Long userId) {
        List<PaymentServiceResponseDTO> serviceResponseDTOs = paymentService.getAllPayments(userId);

        // Service DTO를 Controller DTO로 변환
        List<PaymentResponseDTO> responseDTOs = serviceResponseDTOs.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responseDTOs);
    }

    /**
     * 특정 결제 정보 조회
     * GET /api/user/{userId}/payment/{paymentId}
     */
    @GetMapping("/{paymentId}")
    public ResponseEntity<PaymentResponseDTO> getPaymentById(
            @PathVariable Long userId,
            @PathVariable Long paymentId) {

        PaymentServiceResponseDTO serviceResponseDTO = paymentService.getPaymentById(userId, paymentId);

        // Service DTO를 Controller DTO로 변환
        PaymentResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 결제 정보 업데이트
     * PUT /api/user/{userId}/payment/{paymentId}
     */
    @PutMapping("/{paymentId}")
    public ResponseEntity<PaymentResponseDTO> updatePayment(
            @PathVariable Long userId,
            @PathVariable Long paymentId,
            @Valid @RequestBody PaymentRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        PaymentServiceRequestDTO serviceRequestDTO = PaymentServiceRequestDTO.builder()
                .status(requestDTO.getStatus())
                .paymentAmount(requestDTO.getPaymentAmount())
                .build();

        PaymentServiceResponseDTO serviceResponseDTO = paymentService.updatePayment(userId, paymentId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        PaymentResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 결제 정보 삭제
     * DELETE /api/user/{userId}/payment/{paymentId}
     */
    @DeleteMapping("/{paymentId}")
    public ResponseEntity<Void> deletePayment(
            @PathVariable Long userId,
            @PathVariable Long paymentId) {

        paymentService.deletePayment(userId, paymentId);
        return ResponseEntity.noContent().build();
    }

    private PaymentResponseDTO mapToResponseDTO(PaymentServiceResponseDTO serviceResponseDTO) {
        return PaymentResponseDTO.builder()
                .paymentId(serviceResponseDTO.getPaymentId())
                .userId(serviceResponseDTO.getUserId())
                .status(serviceResponseDTO.getStatus())
                .paymentAmount(serviceResponseDTO.getPaymentAmount())
                .paymentDate(serviceResponseDTO.getPaymentDate())
                .build();
    }
}