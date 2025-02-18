package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.Review;
import com.itsmenlp.foodly.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    List<Review> findByProduct(Product product);
}