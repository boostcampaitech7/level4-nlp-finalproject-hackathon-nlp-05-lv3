package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.ImageToTextServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.ImageToTextServiceResponseDTO;
import org.springframework.stereotype.Service;

@Service
public interface ImageToTextService {
    ImageToTextServiceResponseDTO processInput(ImageToTextServiceRequestDTO serviceRequest);

}