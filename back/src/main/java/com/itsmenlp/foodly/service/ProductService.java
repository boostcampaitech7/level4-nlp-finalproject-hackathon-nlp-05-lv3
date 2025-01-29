package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.ProductCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductResponseServiceDTO;
import com.itsmenlp.foodly.service.dto.ProductUpdateRequestDTO;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

public interface ProductService {
    ProductResponseServiceDTO createProduct(ProductCreateRequestDTO dto);
    ProductResponseServiceDTO getProductById(Long productId);
    List<ProductResponseServiceDTO> getAllProducts();
    List<ProductResponseServiceDTO> getProductsByCategoryId(Long categoryId);
    ProductResponseServiceDTO updateProduct(Long productId, ProductUpdateRequestDTO dto);
    void deleteProduct(Long productId);
    List<ProductResponseServiceDTO> getProductsByName(String name);
}