package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory_CategoryId(Long categoryId);
    List<Product> findByNameContaining(String name);

}