package com.itsmenlp.foodly.controller.dto;

import lombok.Data;

import java.util.List;

@Data
public class ImageToTextResponseDTO {
    private Long id;
    private String link;
    private List<String> images;
    private List<String> texts;
}