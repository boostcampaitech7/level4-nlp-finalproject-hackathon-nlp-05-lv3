package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.CategoryCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.CategoryUpdateRequestDTO;

import java.util.List;

public interface CategoryService {
    CategoryServiceResponseDTO createCategory(CategoryCreateRequestDTO dto);
    CategoryServiceResponseDTO getCategoryById(Long categoryId);
    List<CategoryServiceResponseDTO> getAllCategories();
    CategoryServiceResponseDTO updateCategory(Long categoryId, CategoryUpdateRequestDTO dto);
    void deleteCategory(Long categoryId);
}