package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.ProductRank;
import com.itsmenlp.foodly.entity.ProductRankId;
import com.itsmenlp.foodly.repository.ProductRankRepository;
import com.itsmenlp.foodly.service.dto.ProductRankRequestDTO;
import com.itsmenlp.foodly.service.dto.ProductRankResponseDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public interface ProductRankService {
    ProductRankResponseDTO createProductRank(ProductRankRequestDTO requestDto);
    ProductRankResponseDTO getProductRank(Integer productRankId, Integer productId, Integer aspectId, Integer categoryId);
    ProductRankResponseDTO updateProductRank(Integer productRankId, Integer productId, Integer aspectId, Integer categoryId, ProductRankRequestDTO requestDto);
    void deleteProductRank(Integer productRankId, Integer productId, Integer aspectId, Integer categoryId);

    List<ProductRankResponseDTO> getAllProductRanks();
    List<ProductRankResponseDTO> getProductRanksByAspect(Integer aspectId);
}