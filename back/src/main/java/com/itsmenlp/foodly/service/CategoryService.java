package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.CategoryCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryResponseServiceDTO;
import com.itsmenlp.foodly.service.dto.CategoryUpdateRequestDTO;

import java.util.List;

public interface CategoryService {
    CategoryResponseServiceDTO createCategory(CategoryCreateRequestDTO dto);
    CategoryResponseServiceDTO getCategoryById(Long categoryId);
    List<CategoryResponseServiceDTO> getAllCategories();
    CategoryResponseServiceDTO updateCategory(Long categoryId, CategoryUpdateRequestDTO dto);
    void deleteCategory(Long categoryId);
}