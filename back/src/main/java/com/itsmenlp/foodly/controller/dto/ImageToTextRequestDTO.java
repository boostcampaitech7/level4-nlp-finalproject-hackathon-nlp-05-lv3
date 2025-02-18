package com.itsmenlp.foodly.controller.dto;

import lombok.Data;

import java.util.List;

@Data
public class ImageToTextRequestDTO {
    private String link;
    private List<String> images;
}