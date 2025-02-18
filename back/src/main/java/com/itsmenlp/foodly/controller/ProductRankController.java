package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.ProductRankRequestDTO;
import com.itsmenlp.foodly.controller.dto.ProductRankResponseDTO;
import com.itsmenlp.foodly.service.ProductRankService;
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
    private ProductRankResponseDTO convertToResponse(com.itsmenlp.foodly.service.dto.ProductRankResponseDTO dto) {
        return new ProductRankResponseDTO(
                dto.getProductRankId(),
                dto.getProductId(),
                dto.getAspectId(),
                dto.getCategoryId(),
                dto.getProductRank()
        );
    }

    // 등록 (Create)
    @PostMapping
    public ProductRankResponseDTO createProductRank(@RequestBody ProductRankRequestDTO request) {
        com.itsmenlp.foodly.service.dto.ProductRankRequestDTO requestDTO = new com.itsmenlp.foodly.service.dto.ProductRankRequestDTO(
                request.getProductRankId(),
                request.getProductId(),
                request.getAspectId(),
                request.getCategoryId(),
                request.getProductRank()
        );
        com.itsmenlp.foodly.service.dto.ProductRankResponseDTO responseDTO = productRankService.createProductRank(requestDTO);
        return convertToResponse(responseDTO);
    }

    // 전체 목록 조회 (Read All)
    @GetMapping
    public List<ProductRankResponseDTO> getAllProductRanks() {
        return productRankService.getAllProductRanks()
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    // 단건 조회 (Read)
    @GetMapping("/{productRankId}/{productId}/{aspectId}/{categoryId}")
    public ProductRankResponseDTO getProductRank(
            @PathVariable Integer productRankId,
            @PathVariable Integer productId,
            @PathVariable Integer aspectId,
            @PathVariable Integer categoryId) {
        com.itsmenlp.foodly.service.dto.ProductRankResponseDTO responseDTO = productRankService.getProductRank(productRankId, productId, aspectId, categoryId);
        return convertToResponse(responseDTO);
    }

    // 수정 (Update)
    @PutMapping("/{productRankId}/{productId}/{aspectId}/{categoryId}")
    public ProductRankResponseDTO updateProductRank(
            @PathVariable Integer productRankId,
            @PathVariable Integer productId,
            @PathVariable Integer aspectId,
            @PathVariable Integer categoryId,
            @RequestBody ProductRankRequestDTO request) {
        com.itsmenlp.foodly.service.dto.ProductRankRequestDTO requestDto = new com.itsmenlp.foodly.service.dto.ProductRankRequestDTO(
                request.getProductRankId(),
                request.getProductId(),
                request.getAspectId(),
                request.getCategoryId(),
                request.getProductRank()
        );
        com.itsmenlp.foodly.service.dto.ProductRankResponseDTO responseDTO = productRankService.updateProductRank(productRankId, productId, aspectId, categoryId, requestDto);
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
    public List<ProductRankResponseDTO> getProductRanksByAspect(@PathVariable Integer aspectId) {
        return productRankService.getProductRanksByAspect(aspectId)
                .stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }
}