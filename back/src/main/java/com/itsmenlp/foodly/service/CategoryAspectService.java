package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.CategoryAspectCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectResponseServiceDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectUpdateRequestDTO;

import java.util.List;

public interface CategoryAspectService {
    CategoryAspectResponseServiceDTO createAspect(Long categoryId, CategoryAspectCreateRequestDTO dto);
    CategoryAspectResponseServiceDTO getAspectById(Long aspectId);
    List<CategoryAspectResponseServiceDTO> getAllAspectsByCategory(Long categoryId);
    CategoryAspectResponseServiceDTO updateAspect(Long aspectId, CategoryAspectUpdateRequestDTO dto);
    void deleteAspect(Long aspectId);
}