package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.CategoryAspectCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectUpdateRequestDTO;

import java.util.List;

public interface CategoryAspectService {
    CategoryAspectServiceResponseDTO createAspect(Long categoryId, CategoryAspectCreateRequestDTO dto);
    CategoryAspectServiceResponseDTO getAspectById(Long aspectId);
    List<CategoryAspectServiceResponseDTO> getAllAspectsByCategory(Long categoryId);
    CategoryAspectServiceResponseDTO updateAspect(Long aspectId, CategoryAspectUpdateRequestDTO dto);
    void deleteAspect(Long aspectId);
}