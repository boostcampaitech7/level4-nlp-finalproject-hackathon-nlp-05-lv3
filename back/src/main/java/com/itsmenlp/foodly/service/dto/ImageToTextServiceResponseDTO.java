package com.itsmenlp.foodly.service.dto;

import lombok.Data;

import java.util.List;

@Data
public class ImageToTextServiceResponseDTO {
    private Long id;
    private String link;
    private List<String> inputImages;
    private List<String> outputTexts;
}