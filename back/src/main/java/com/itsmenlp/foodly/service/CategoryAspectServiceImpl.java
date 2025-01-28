package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Category;
import com.itsmenlp.foodly.entity.CategoryAspect;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.CategoryAspectRepository;
import com.itsmenlp.foodly.repository.CategoryRepository;
import com.itsmenlp.foodly.service.dto.CategoryAspectCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectResponseServiceDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectUpdateRequestDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class CategoryAspectServiceImpl implements CategoryAspectService {

    private final CategoryAspectRepository aspectRepository;
    private final CategoryRepository categoryRepository;

    @Autowired
    public CategoryAspectServiceImpl(CategoryAspectRepository aspectRepository, CategoryRepository categoryRepository) {
        this.aspectRepository = aspectRepository;
        this.categoryRepository = categoryRepository;
    }

    @Override
    public CategoryAspectResponseServiceDTO createAspect(Long categoryId, CategoryAspectCreateRequestDTO dto) {
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id " + categoryId));

        CategoryAspect aspect = CategoryAspect.builder()
                .aspect(dto.getAspect())
                .category(category)
                .build();

        CategoryAspect savedAspect = aspectRepository.save(aspect);
        return mapToResponseDTO(savedAspect);
    }

    @Override
    @Transactional(readOnly = true)
    public CategoryAspectResponseServiceDTO getAspectById(Long aspectId) {
        CategoryAspect aspect = aspectRepository.findById(aspectId)
                .orElseThrow(() -> new ResourceNotFoundException("Aspect not found with id " + aspectId));
        return mapToResponseDTO(aspect);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CategoryAspectResponseServiceDTO> getAllAspectsByCategory(Long categoryId) {
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id " + categoryId));

        return category.getAspects().stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    public CategoryAspectResponseServiceDTO updateAspect(Long aspectId, CategoryAspectUpdateRequestDTO dto) {
        CategoryAspect aspect = aspectRepository.findById(aspectId)
                .orElseThrow(() -> new ResourceNotFoundException("Aspect not found with id " + aspectId));
        aspect.setAspect(dto.getAspect());
        CategoryAspect updatedAspect = aspectRepository.save(aspect);
        return mapToResponseDTO(updatedAspect);
    }

    @Override
    public void deleteAspect(Long aspectId) {
        if (!aspectRepository.existsById(aspectId)) {
            throw new ResourceNotFoundException("Aspect not found with id " + aspectId);
        }
        aspectRepository.deleteById(aspectId);
    }

    private CategoryAspectResponseServiceDTO mapToResponseDTO(CategoryAspect aspect) {
        return CategoryAspectResponseServiceDTO.builder()
                .id(aspect.getId())
                .aspect(aspect.getAspect())
                .build();
    }
}