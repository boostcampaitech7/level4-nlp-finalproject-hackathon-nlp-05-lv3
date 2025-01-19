package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.ImageToText;
import com.itsmenlp.foodly.repository.ImageToTextRepository;
import com.itsmenlp.foodly.service.dto.ImageToTextServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.ImageToTextServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.ProcessImageToTextResponseDTO;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ImageToTextService {

    private final ImageToTextRepository imageToTextRepository;
    private final RestTemplate restTemplate;

    public ImageToTextService(ImageToTextRepository imageToTextRepository) {
        this.imageToTextRepository = imageToTextRepository;
        this.restTemplate = new RestTemplate();
    }

    public ImageToTextServiceResponseDTO processInput(ImageToTextServiceRequestDTO serviceRequest) {
        // 1. 입력 데이터를 엔티티로 변환하여 저장
        ImageToText entity = new ImageToText();
        entity.setLink(serviceRequest.getLink());
        entity.setInputImages(serviceRequest.getImages());
        ImageToText savedEntity = imageToTextRepository.save(entity);

        // 2. 외부 API 호출 (예: http://127.0.0.1:5001/process)
        String externalApiUrl = "http://127.0.0.1:5001/process";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        // 외부 API 요청시 serviceRequest의 구조(예, link와 images)를 그대로 사용한다고 가정
        HttpEntity<ImageToTextServiceRequestDTO> requestEntity = new HttpEntity<>(serviceRequest, headers);
        ResponseEntity<ProcessImageToTextResponseDTO> responseEntity = restTemplate.postForEntity(
                externalApiUrl,
                requestEntity,
                ProcessImageToTextResponseDTO.class
        );

        ProcessImageToTextResponseDTO externalResponse = responseEntity.getBody();
        if (externalResponse == null || externalResponse.getTexts() == null) {
            throw new RuntimeException("Invalid response from external API");
        }

        // 3. 외부 API로부터 받은 texts를 엔티티에 업데이트 후 저장
        savedEntity.setOutputTexts(externalResponse.getTexts());
        imageToTextRepository.save(savedEntity);

        // 4. 서비스 응답 DTO로 변환
        ImageToTextServiceResponseDTO serviceResponse = new ImageToTextServiceResponseDTO();
        serviceResponse.setId(savedEntity.getId());
        serviceResponse.setLink(savedEntity.getLink());
        serviceResponse.setInputImages(savedEntity.getInputImages());
        serviceResponse.setOutputTexts(savedEntity.getOutputTexts());
        return serviceResponse;
    }
}