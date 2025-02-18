package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.OrderServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.OrderServiceResponseDTO;

import java.util.List;

public interface OrderService {

    OrderServiceResponseDTO createOrder(Long userId, OrderServiceRequestDTO requestDTO);

    List<OrderServiceResponseDTO> getAllOrders(Long userId);

    OrderServiceResponseDTO getOrderById(Long userId, Long orderId);

    OrderServiceResponseDTO updateOrder(Long userId, Long orderId, OrderServiceRequestDTO requestDTO);

    void deleteOrder(Long userId, Long orderId);
}