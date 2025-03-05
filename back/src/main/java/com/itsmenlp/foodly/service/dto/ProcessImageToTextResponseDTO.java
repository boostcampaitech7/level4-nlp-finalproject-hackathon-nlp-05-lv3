package com.itsmenlp.foodly.service.dto;

import lombok.Data;

import java.util.List;

@Data
public class ProcessImageToTextResponseDTO {
    private List<String> texts;
}