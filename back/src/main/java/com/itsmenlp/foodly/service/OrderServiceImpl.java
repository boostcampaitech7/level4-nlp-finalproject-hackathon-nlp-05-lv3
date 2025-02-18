package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.*;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.*;
import com.itsmenlp.foodly.service.dto.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final UserRepository userRepository;
    private final PaymentRepository paymentRepository;
    private final AddressRepository addressRepository;
    private final ProductRepository productRepository;
    private final CartRepository cartRepository;

    @Override
    @Transactional
    public OrderServiceResponseDTO createOrder(Long userId, OrderServiceRequestDTO requestDTO) {
        User user = getUserById(userId);
        Payment payment = getPaymentByIdAndUser(requestDTO.getPaymentId(), user);
        Address address = getAddressByIdAndUser(requestDTO.getAddressId(), user);

        Order order = Order.builder()
                .user(user)
                .payment(payment)
                .address(address)
                .orderStatus(requestDTO.getOrderStatus())
                .totalAmount(requestDTO.getTotalAmount())
                .build();

        Order savedOrder = orderRepository.save(order);

        List<OrderItemServiceRequestDTO> orderItemsDTO = requestDTO.getOrderItems();

        List<OrderItem> orderItems = orderItemsDTO.stream()
                .map(itemDTO -> {
                    Product product = getProductById(itemDTO.getProductId());
                    return OrderItem.builder()
                            .order(savedOrder)
                            .product(product)
                            .quantity(itemDTO.getQuantity())
                            .unitPrice(itemDTO.getUnitPrice())
                            .build();
                })
                .collect(Collectors.toList());

        orderItemRepository.saveAll(orderItems);

        savedOrder.setOrderItems(orderItems);

        return mapToServiceResponseDTO(savedOrder);
    }

    @Override
    @Transactional(readOnly = true)
    public List<OrderServiceResponseDTO> getAllOrders(Long userId) {
        User user = getUserById(userId);
        List<Order> orders = orderRepository.findByUser(user);

        return orders.stream()
                .map(this::mapToServiceResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public OrderServiceResponseDTO getOrderById(Long userId, Long orderId) {
        User user = getUserById(userId);
        Order order = getOrderByIdAndUser(orderId, user);

        return mapToServiceResponseDTO(order);
    }

    @Override
    @Transactional
    public OrderServiceResponseDTO updateOrder(Long userId, Long orderId, OrderServiceRequestDTO requestDTO) {
        User user = getUserById(userId);
        Order order = getOrderByIdAndUser(orderId, user);

        Payment payment = getPaymentByIdAndUser(requestDTO.getPaymentId(), user);
        Address address = getAddressByIdAndUser(requestDTO.getAddressId(), user);

        order.setPayment(payment);
        order.setAddress(address);
        order.setOrderStatus(requestDTO.getOrderStatus());
        order.setTotalAmount(requestDTO.getTotalAmount());

        // 기존 주문 항목 삭제
        orderItemRepository.deleteAll(order.getOrderItems());

        // 새로운 주문 항목 추가
        List<OrderItemServiceRequestDTO> orderItemsDTO = requestDTO.getOrderItems();

        List<OrderItem> orderItems = orderItemsDTO.stream()
                .map(itemDTO -> {
                    Product product = getProductById(itemDTO.getProductId());
                    return OrderItem.builder()
                            .order(order)
                            .product(product)
                            .quantity(itemDTO.getQuantity())
                            .unitPrice(itemDTO.getUnitPrice())
                            .build();
                })
                .collect(Collectors.toList());

        orderItemRepository.saveAll(orderItems);

        order.setOrderItems(orderItems);

        Order updatedOrder = orderRepository.save(order);

        return mapToServiceResponseDTO(updatedOrder);
    }

    @Override
    @Transactional
    public void deleteOrder(Long userId, Long orderId) {
        User user = getUserById(userId);
        Order order = getOrderByIdAndUser(orderId, user);

        orderRepository.delete(order);
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

    private Address getAddressByIdAndUser(Long addressId, User user) {
        return addressRepository.findById(addressId)
                .filter(address -> address.getUser().equals(user))
                .orElseThrow(() -> new ResourceNotFoundException("Address not found with id: " + addressId + " for user id: " + user.getUserId()));
    }

    private Product getProductById(Long productId) {
        return productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + productId));
    }

    private Order getOrderByIdAndUser(Long orderId, User user) {
        return orderRepository.findById(orderId)
                .filter(order -> order.getUser().equals(user))
                .orElseThrow(() -> new ResourceNotFoundException("Order not found with id: " + orderId + " for user id: " + user.getUserId()));
    }

    private OrderServiceResponseDTO mapToServiceResponseDTO(Order order) {
        List<OrderItemServiceResponseDTO> orderItemsDTO = order.getOrderItems().stream()
                .map(item -> OrderItemServiceResponseDTO.builder()
                        .orderItemId(item.getOrderItemId())
                        .productId(item.getProduct().getProductId())
                        .productName(item.getProduct().getName())
                        .quantity(item.getQuantity())
                        .unitPrice(item.getUnitPrice())
                        .build())
                .collect(Collectors.toList());

        return OrderServiceResponseDTO.builder()
                .orderId(order.getOrderId())
                .userId(order.getUser().getUserId())
                .paymentId(order.getPayment().getPaymentId())
                .addressId(order.getAddress().getAddressId())
                .orderStatus(order.getOrderStatus())
                .totalAmount(order.getTotalAmount())
                .createdAt(order.getCreatedAt())
                .updatedAt(order.getUpdatedAt())
                .orderItems(orderItemsDTO)
                .build();
    }
}