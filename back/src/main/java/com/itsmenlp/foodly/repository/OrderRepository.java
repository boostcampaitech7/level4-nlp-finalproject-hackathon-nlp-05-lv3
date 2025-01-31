package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.Order;
import com.itsmenlp.foodly.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    List<Order> findByUser(User user);
}