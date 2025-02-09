package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.ProductRequestDTO;
import com.itsmenlp.foodly.controller.dto.ProductResponseDTO;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.service.ProductService;
import com.itsmenlp.foodly.service.dto.ProductCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.ProductUpdateRequestDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/product")
public class ProductController {

    private final ProductService productService;

    @Autowired
    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    // 상품 생성
    @PostMapping
    public ResponseEntity<ProductResponseDTO> createProduct(@Validated @RequestBody ProductRequestDTO productRequestDTO) {
        ProductCreateRequestDTO createDTO = ProductCreateRequestDTO.builder()
                .categoryId(productRequestDTO.getCategoryId())
                .name(productRequestDTO.getName())
                .thumbnailUrl(productRequestDTO.getThumbnailUrl())
                .thumbnailCaption(productRequestDTO.getThumbnailCaption())
                .mall(productRequestDTO.getMall())
                .price(productRequestDTO.getPrice())
                .stock(productRequestDTO.getStock())
                .rating(productRequestDTO.getRating())
                .coupon(productRequestDTO.getCoupon())
                .delivery(productRequestDTO.getDelivery())
                .build();
        ProductServiceResponseDTO serviceResponse = productService.createProduct(createDTO);
        ProductResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    // 특정 상품 조회
    @GetMapping("/{id:\\d+}")
    public ResponseEntity<ProductResponseDTO> getProductById(@PathVariable("id") Long productId) {
        ProductServiceResponseDTO serviceResponse = productService.getProductById(productId);
        ProductResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    // 모든 상품 조회
    @GetMapping
    public ResponseEntity<List<ProductResponseDTO>> getAllProducts() {
        List<ProductServiceResponseDTO> serviceResponses = productService.getAllProducts();
        List<ProductResponseDTO> responseDTOs = serviceResponses.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responseDTOs);
    }

    // 특정 카테고리의 상품 조회
    @GetMapping("/categories/{categoryId}")
    public ResponseEntity<List<ProductResponseDTO>> getProductsByCategoryId(@PathVariable("categoryId") Long categoryId) {
        List<ProductServiceResponseDTO> serviceResponses = productService.getProductsByCategoryId(categoryId);
        List<ProductResponseDTO> responseDTOs = serviceResponses.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responseDTOs);
    }

    // 상품 업데이트
    @PutMapping("/{id}")
    public ResponseEntity<ProductResponseDTO> updateProduct(
            @PathVariable("id") Long productId,
            @Validated @RequestBody ProductRequestDTO productRequestDTO) {
        ProductUpdateRequestDTO updateDTO = ProductUpdateRequestDTO.builder()
                .categoryId(productRequestDTO.getCategoryId())
                .name(productRequestDTO.getName())
                .thumbnailUrl(productRequestDTO.getThumbnailUrl())
                .thumbnailCaption(productRequestDTO.getThumbnailCaption())
                .mall(productRequestDTO.getMall())
                .price(productRequestDTO.getPrice())
                .stock(productRequestDTO.getStock())
                .rating(productRequestDTO.getRating())
                .coupon(productRequestDTO.getCoupon())
                .delivery(productRequestDTO.getDelivery())
                .build();
        ProductServiceResponseDTO serviceResponse = productService.updateProduct(productId, updateDTO);
        ProductResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    // 상품 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable("id") Long productId) {
        productService.deleteProduct(productId);
        return ResponseEntity.noContent().build();
    }

    // DTO 매핑 메서드
    private ProductResponseDTO mapToResponseDTO(ProductServiceResponseDTO serviceResponse) {
        return ProductResponseDTO.builder()
                .productId(serviceResponse.getProductId())
                .categoryId(serviceResponse.getCategoryId())
                .name(serviceResponse.getName())
                .thumbnailUrl(serviceResponse.getThumbnailUrl())
                .thumbnailCaption(serviceResponse.getThumbnailCaption())
                .mall(serviceResponse.getMall())
                .price(serviceResponse.getPrice())
                .stock(serviceResponse.getStock())
                .rating(serviceResponse.getRating())
                .coupon(serviceResponse.getCoupon())
                .delivery(serviceResponse.getDelivery())
                .createdAt(serviceResponse.getCreatedAt())
                .updatedAt(serviceResponse.getUpdatedAt())
                .build();
    }

    // (예시) 이름 검색
    @GetMapping("/search")
    public ResponseEntity<List<ProductResponseDTO>> getProductsByName(@RequestParam("name") String name) {
        // Service를 통해 검색
        List<ProductServiceResponseDTO> serviceResponses = productService.getProductsByName(name);

        // Controller에서 쓰는 DTO로 변환
        List<ProductResponseDTO> responseDTOs = serviceResponses.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responseDTOs);
    }

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<String> handleResourceNotFound(ResourceNotFoundException ex){
        return new ResponseEntity<>(ex.getMessage(), HttpStatus.NOT_FOUND);
    }
}