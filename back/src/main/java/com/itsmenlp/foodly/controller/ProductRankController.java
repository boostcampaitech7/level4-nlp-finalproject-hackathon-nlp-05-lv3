package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.ProductRankRequest;
import com.itsmenlp.foodly.controller.dto.ProductRankResponse;
import com.itsmenlp.foodly.service.ProductRankService;
import com.itsmenlp.foodly.service.dto.ProductRankRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductRankResponseDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/rank")
public class ProductRankController {

    @Autowired
    private ProductRankService productRankService;

    // Service DTO -> Controller DTO 변환
    private ProductRankResponse convertToResponse(ProductRankResponseDTO dto) {
        return new ProductRankResponse(
                dto.getProductRankId(),
                dto.getProductId(),
                dto.getAspectId(),
                dto.getCategoryId(),
                dto.getProductRank()
        );
    }

    // 등록 (Create)
    @PostMapping
    public ProductRankResponse createProductRank(@RequestBody ProductRankRequest request) {
        ProductRankRequestDTO requestDTO = new ProductRankRequestDTO(
                request.getProductRankId(),
                request.getProductId(),
                request.getAspectId(),
                request.getCategoryId(),
                request.getProductRank()
        );
        ProductRankResponseDTO responseDTO = productRankService.createProductRank(requestDTO);
        return convertToResponse(responseDTO);
    }

    // 전체 목록 조회 (Read All)
    @GetMapping
    public List<ProductRankResponse> getAllProductRanks() {
        return productRankService.getAllProductRanks()
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    // 단건 조회 (Read)
    @GetMapping("/{productRankId}/{productId}/{aspectId}/{categoryId}")
    public ProductRankResponse getProductRank(
            @PathVariable Integer productRankId,
            @PathVariable Integer productId,
            @PathVariable Integer aspectId,
            @PathVariable Integer categoryId) {
        ProductRankResponseDTO responseDTO = productRankService.getProductRank(productRankId, productId, aspectId, categoryId);
        return convertToResponse(responseDTO);
    }

    // 수정 (Update)
    @PutMapping("/{productRankId}/{productId}/{aspectId}/{categoryId}")
    public ProductRankResponse updateProductRank(
            @PathVariable Integer productRankId,
            @PathVariable Integer productId,
            @PathVariable Integer aspectId,
            @PathVariable Integer categoryId,
            @RequestBody ProductRankRequest request) {
        ProductRankRequestDTO requestDto = new ProductRankRequestDTO(
                request.getProductRankId(),
                request.getProductId(),
                request.getAspectId(),
                request.getCategoryId(),
                request.getProductRank()
        );
        ProductRankResponseDTO responseDTO = productRankService.updateProductRank(productRankId, productId, aspectId, categoryId, requestDto);
        return convertToResponse(responseDTO);
    }

    // 삭제 (Delete)
    @DeleteMapping("/{productRankId}/{productId}/{aspectId}/{categoryId}")
    public void deleteProductRank(
            @PathVariable Integer productRankId,
            @PathVariable Integer productId,
            @PathVariable Integer aspectId,
            @PathVariable Integer categoryId) {
        productRankService.deleteProductRank(productRankId, productId, aspectId, categoryId);
    }

    // 특정 aspect_id의 데이터를 rank(=COUNT) 내림차순 정렬하여 조회
    @GetMapping("/aspect/{aspectId}")
    public List<ProductRankResponse> getProductRanksByAspect(@PathVariable Integer aspectId) {
        return productRankService.getProductRanksByAspect(aspectId)
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
}