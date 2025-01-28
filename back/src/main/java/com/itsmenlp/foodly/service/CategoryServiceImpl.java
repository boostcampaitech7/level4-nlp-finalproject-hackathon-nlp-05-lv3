package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Category;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.CategoryRepository;
import com.itsmenlp.foodly.service.dto.CategoryAspectResponseServiceDTO;
import com.itsmenlp.foodly.service.dto.CategoryCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryResponseServiceDTO;
import com.itsmenlp.foodly.service.dto.CategoryUpdateRequestDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class CategoryServiceImpl implements CategoryService {

    private final CategoryRepository categoryRepository;

    @Autowired
    public CategoryServiceImpl(CategoryRepository categoryRepository) {
        this.categoryRepository = categoryRepository;
    }

    @Override
    public CategoryResponseServiceDTO createCategory(CategoryCreateRequestDTO dto) {
        Category category = Category.builder()
                .name(dto.getName())
                .build();
        Category savedCategory = categoryRepository.save(category);
        return mapToResponseDTO(savedCategory);
    }

    @Override
    @Transactional(readOnly = true)
    public CategoryResponseServiceDTO getCategoryById(Long categoryId) {
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id " + categoryId));
        return mapToResponseDTO(category);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CategoryResponseServiceDTO> getAllCategories() {
        List<Category> categories = categoryRepository.findAll();
        return categories.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    public CategoryResponseServiceDTO updateCategory(Long categoryId, CategoryUpdateRequestDTO dto) {
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id " + categoryId));
        category.setName(dto.getName());
        Category updatedCategory = categoryRepository.save(category);
        return mapToResponseDTO(updatedCategory);
    }

    @Override
    public void deleteCategory(Long categoryId) {
        if (!categoryRepository.existsById(categoryId)) {
            throw new ResourceNotFoundException("Category not found with id " + categoryId);
        }
        categoryRepository.deleteById(categoryId);
    }

    private CategoryResponseServiceDTO mapToResponseDTO(Category category) {
        List<CategoryAspectResponseServiceDTO> aspectDTOs = category.getAspects().stream()
                .map(aspect -> CategoryAspectResponseServiceDTO.builder()
                        .id(aspect.getId())
                        .aspect(aspect.getAspect())
                        .build())
                .collect(Collectors.toList());

        return CategoryResponseServiceDTO.builder()
                .categoryId(category.getCategoryId())
                .name(category.getName())
                .createdAt(category.getCreatedAt())
                .updatedAt(category.getUpdatedAt())
                .aspects(aspectDTOs)
                .build();
    }
}