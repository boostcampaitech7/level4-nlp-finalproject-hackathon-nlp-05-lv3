package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.OrderItem;
import com.itsmenlp.foodly.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {

    List<OrderItem> findByOrder(Order order);
}