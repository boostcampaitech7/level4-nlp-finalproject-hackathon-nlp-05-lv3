package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.DescriptionServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.DescriptionServiceResponseDTO;

public interface DescriptionService {

    DescriptionServiceResponseDTO createDescription(Long productId, DescriptionServiceRequestDTO requestDTO);
    DescriptionServiceResponseDTO getDescription(Long productId);
    DescriptionServiceResponseDTO updateDescription(Long productId, DescriptionServiceRequestDTO requestDTO);
    void deleteDescription(Long productId);
}