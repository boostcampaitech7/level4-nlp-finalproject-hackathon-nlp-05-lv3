package com.itsmenlp.foodly.service.dto;

import lombok.Data;

import java.util.List;

@Data
public class ImageToTextServiceRequestDTO {
    private String link;
    private List<String> images;
}