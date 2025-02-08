package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.ImageToTextRequestDTO;
import com.itsmenlp.foodly.controller.dto.ImageToTextResponseDTO;
import com.itsmenlp.foodly.service.ImageToTextService;
import com.itsmenlp.foodly.service.dto.ImageToTextServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.ImageToTextServiceResponseDTO;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/image-to-text")
public class ImageToTextController {

    private final ImageToTextService imageToTextService;

    public ImageToTextController(ImageToTextService imageToTextService) {
        this.imageToTextService = imageToTextService;
    }

    @PostMapping("/process")
    public ResponseEntity<ImageToTextResponseDTO> process(@RequestBody ImageToTextRequestDTO request) {
        // Controller DTO -> Service DTO 매핑
        ImageToTextServiceRequestDTO serviceRequest = new ImageToTextServiceRequestDTO();
        serviceRequest.setLink(request.getLink());
        serviceRequest.setImages(request.getImages());

        ImageToTextServiceResponseDTO serviceResponse = imageToTextService.processInput(serviceRequest);

        // Service DTO -> Controller DTO 매핑
        ImageToTextResponseDTO response = new ImageToTextResponseDTO();
        response.setId(serviceResponse.getId());
        response.setLink(serviceResponse.getLink());
        response.setImages(serviceResponse.getInputImages());
        response.setTexts(serviceResponse.getOutputTexts());

        return ResponseEntity.ok(response);
    }
}