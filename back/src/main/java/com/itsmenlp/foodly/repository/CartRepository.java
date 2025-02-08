package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.Cart;
import com.itsmenlp.foodly.entity.Product;
import com.itsmenlp.foodly.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CartRepository extends JpaRepository<Cart, Long> {

    List<Cart> findByUser(User user);

    Optional<Cart> findByCartIdAndUser(Long cartId, User user);

    boolean existsByProductAndUser(Product product, User user);
}