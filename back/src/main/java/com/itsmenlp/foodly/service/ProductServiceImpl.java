package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Category;
import com.itsmenlp.foodly.entity.Product;
import com.itsmenlp.foodly.repository.CategoryRepository;
import com.itsmenlp.foodly.repository.ProductRepository;
import com.itsmenlp.foodly.service.dto.ProductCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.ProductUpdateRequestDTO;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class ProductServiceImpl implements ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;

    @Autowired
    public ProductServiceImpl(ProductRepository productRepository, CategoryRepository categoryRepository) {
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }

    @Override
    public ProductServiceResponseDTO createProduct(ProductCreateRequestDTO dto) {
        Category category = categoryRepository.findById(dto.getCategoryId())
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id " + dto.getCategoryId()));

        Product product = Product.builder()
                .category(category)
                .name(dto.getName())
                .thumbnailUrl(dto.getThumbnailUrl())
                .thumbnailCaption(dto.getThumbnailCaption())
                .thumbnailCaptionShort(dto.getThumbnailCaptionShort())
                .mall(dto.getMall())
                .price(dto.getPrice())
                .stock(dto.getStock() != null ? dto.getStock() : 10)
                .rating(dto.getRating())
                .coupon(dto.getCoupon())
                .delivery(dto.getDelivery())
                .build();

        Product savedProduct = productRepository.save(product);
        return mapToResponseDTO(savedProduct);
    }

    @Override
    @Transactional(readOnly = true)
    public ProductServiceResponseDTO getProductById(Long productId) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id " + productId));
        return mapToResponseDTO(product);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ProductServiceResponseDTO> getAllProducts() {
        List<Product> products = productRepository.findAll();
        return products.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<ProductServiceResponseDTO> getProductsByCategoryId(Long categoryId) {
        List<Product> products = productRepository.findByCategory_CategoryId(categoryId);
        return products.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    public ProductServiceResponseDTO updateProduct(Long productId, ProductUpdateRequestDTO dto) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id " + productId));

        Category category = categoryRepository.findById(dto.getCategoryId())
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id " + dto.getCategoryId()));

        product.setCategory(category);
        product.setName(dto.getName());
        product.setThumbnailUrl(dto.getThumbnailUrl());
        product.setThumbnailCaption(dto.getThumbnailCaption());
        product.setThumbnailCaptionShort(dto.getThumbnailCaptionShort());
        product.setMall(dto.getMall());
        product.setPrice(dto.getPrice());
        product.setStock(dto.getStock() != null ? dto.getStock() : product.getStock());
        product.setRating(dto.getRating());
        product.setCoupon(dto.getCoupon());
        product.setDelivery(dto.getDelivery());

        Product updatedProduct = productRepository.save(product);
        return mapToResponseDTO(updatedProduct);
    }

    @Override
    public void deleteProduct(Long productId) {
        if (!productRepository.existsById(productId)) {
            throw new ResourceNotFoundException("Product not found with id " + productId);
        }
        productRepository.deleteById(productId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ProductServiceResponseDTO> getProductsByName(String name) {
        List<Product> products = productRepository.findByNameContaining(name);
        return products.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    private ProductServiceResponseDTO mapToResponseDTO(Product product) {
        return ProductServiceResponseDTO.builder()
                .productId(product.getProductId())
                .categoryId(product.getCategory() != null ? product.getCategory().getCategoryId() : null)
                .name(product.getName())
                .thumbnailUrl(product.getThumbnailUrl())
                .thumbnailCaption(product.getThumbnailCaption())
                .thumbnailCaptionShort(product.getThumbnailCaptionShort())
                .mall(product.getMall())
                .price(product.getPrice())
                .stock(product.getStock())
                .rating(product.getRating())
                .coupon(product.getCoupon())
                .delivery(product.getDelivery())
                .createdAt(product.getCreatedAt())
                .updatedAt(product.getUpdatedAt())
                .build();
    }
}