package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.DescriptionRequestServiceDTO;
import com.itsmenlp.foodly.service.dto.DescriptionResponseServiceDTO;

public interface DescriptionService {

    DescriptionResponseServiceDTO createDescription(Long productId, DescriptionRequestServiceDTO requestDTO);
    DescriptionResponseServiceDTO getDescription(Long productId);
    DescriptionResponseServiceDTO updateDescription(Long productId, DescriptionRequestServiceDTO requestDTO);
    void deleteDescription(Long productId);
}