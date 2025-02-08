package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.OrderRequestDTO;
import com.itsmenlp.foodly.controller.dto.OrderResponseDTO;
import com.itsmenlp.foodly.service.OrderService;
import com.itsmenlp.foodly.service.dto.OrderServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.OrderServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user/{userId}/order")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    /**
     * 주문 생성
     * POST /api/user/{userId}/order
     */
    @PostMapping
    public ResponseEntity<OrderResponseDTO> createOrder(
            @PathVariable Long userId,
            @Valid @RequestBody OrderRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        OrderServiceRequestDTO serviceRequestDTO = OrderServiceRequestDTO.builder()
                .paymentId(requestDTO.getPaymentId())
                .addressId(requestDTO.getAddressId())
                .orderStatus(requestDTO.getOrderStatus())
                .totalAmount(requestDTO.getTotalAmount())
                .orderItems(
                        requestDTO.getOrderItems().stream()
                                .map(itemDTO -> com.itsmenlp.foodly.service.dto.OrderItemServiceRequestDTO.builder()
                                        .productId(itemDTO.getProductId())
                                        .quantity(itemDTO.getQuantity())
                                        .unitPrice(itemDTO.getUnitPrice())
                                        .build())
                                .collect(Collectors.toList())
                )
                .build();

        OrderServiceResponseDTO serviceResponseDTO = orderService.createOrder(userId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        OrderResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    /**
     * 모든 주문 조회
     * GET /api/user/{userId}/order
     */
    @GetMapping
    public ResponseEntity<List<OrderResponseDTO>> getAllOrders(@PathVariable Long userId) {
        List<OrderServiceResponseDTO> serviceResponseDTOs = orderService.getAllOrders(userId);

        // Service DTO를 Controller DTO로 변환
        List<OrderResponseDTO> responseDTOs = serviceResponseDTOs.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responseDTOs);
    }

    /**
     * 특정 주문 조회
     * GET /api/user/{userId}/order/{orderId}
     */
    @GetMapping("/{orderId}")
    public ResponseEntity<OrderResponseDTO> getOrderById(
            @PathVariable Long userId,
            @PathVariable Long orderId) {

        OrderServiceResponseDTO serviceResponseDTO = orderService.getOrderById(userId, orderId);

        // Service DTO를 Controller DTO로 변환
        OrderResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 주문 업데이트
     * PUT /api/user/{userId}/order/{orderId}
     */
    @PutMapping("/{orderId}")
    public ResponseEntity<OrderResponseDTO> updateOrder(
            @PathVariable Long userId,
            @PathVariable Long orderId,
            @Valid @RequestBody OrderRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        OrderServiceRequestDTO serviceRequestDTO = OrderServiceRequestDTO.builder()
                .paymentId(requestDTO.getPaymentId())
                .addressId(requestDTO.getAddressId())
                .orderStatus(requestDTO.getOrderStatus())
                .totalAmount(requestDTO.getTotalAmount())
                .orderItems(
                        requestDTO.getOrderItems().stream()
                                .map(itemDTO -> com.itsmenlp.foodly.service.dto.OrderItemServiceRequestDTO.builder()
                                        .productId(itemDTO.getProductId())
                                        .quantity(itemDTO.getQuantity())
                                        .unitPrice(itemDTO.getUnitPrice())
                                        .build())
                                .collect(Collectors.toList())
                )
                .build();

        OrderServiceResponseDTO serviceResponseDTO = orderService.updateOrder(userId, orderId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        OrderResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 주문 삭제
     * DELETE /api/user/{userId}/order/{orderId}
     */
    @DeleteMapping("/{orderId}")
    public ResponseEntity<Void> deleteOrder(
            @PathVariable Long userId,
            @PathVariable Long orderId) {

        orderService.deleteOrder(userId, orderId);
        return ResponseEntity.noContent().build();
    }

    private OrderResponseDTO mapToResponseDTO(OrderServiceResponseDTO serviceResponseDTO) {
        List<com.itsmenlp.foodly.controller.dto.OrderItemResponseDTO> orderItemsDTO = serviceResponseDTO.getOrderItems().stream()
                .map(item -> com.itsmenlp.foodly.controller.dto.OrderItemResponseDTO.builder()
                        .orderItemId(item.getOrderItemId())
                        .productId(item.getProductId())
                        .productName(item.getProductName())
                        .quantity(item.getQuantity())
                        .unitPrice(item.getUnitPrice())
                        .build())
                .collect(Collectors.toList());

        return OrderResponseDTO.builder()
                .orderId(serviceResponseDTO.getOrderId())
                .userId(serviceResponseDTO.getUserId())
                .paymentId(serviceResponseDTO.getPaymentId())
                .addressId(serviceResponseDTO.getAddressId())
                .orderStatus(serviceResponseDTO.getOrderStatus())
                .totalAmount(serviceResponseDTO.getTotalAmount())
                .createdAt(serviceResponseDTO.getCreatedAt())
                .updatedAt(serviceResponseDTO.getUpdatedAt())
                .orderItems(orderItemsDTO)
                .build();
    }
}