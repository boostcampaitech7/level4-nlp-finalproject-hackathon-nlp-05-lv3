package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.ProductCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.ProductUpdateRequestDTO;

import java.util.List;

public interface ProductService {
    ProductServiceResponseDTO createProduct(ProductCreateRequestDTO dto);
    ProductServiceResponseDTO getProductById(Long productId);
    List<ProductServiceResponseDTO> getAllProducts();
    List<ProductServiceResponseDTO> getProductsByCategoryId(Long categoryId);
    ProductServiceResponseDTO updateProduct(Long productId, ProductUpdateRequestDTO dto);
    void deleteProduct(Long productId);
    List<ProductServiceResponseDTO> getProductsByName(String name);
}