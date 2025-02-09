package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.CategoryRequestDTO;
import com.itsmenlp.foodly.controller.dto.CategoryResponseDTO;
import com.itsmenlp.foodly.controller.dto.CategoryAspectRequestDTO;
import com.itsmenlp.foodly.controller.dto.CategoryAspectResponseDTO;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.service.CategoryService;
import com.itsmenlp.foodly.service.CategoryAspectService;
import com.itsmenlp.foodly.service.dto.CategoryCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryUpdateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectUpdateRequestDTO;
import com.itsmenlp.foodly.service.dto.CategoryServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.CategoryAspectServiceResponseDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/category")
public class CategoryController {

    private final CategoryService categoryService;
    private final CategoryAspectService categoryAspectService;

    @Autowired
    public CategoryController(CategoryService categoryService, CategoryAspectService categoryAspectService) {
        this.categoryService = categoryService;
        this.categoryAspectService = categoryAspectService;
    }

    // 카테고리 CRUD

    @PostMapping
    public ResponseEntity<CategoryResponseDTO> createCategory(@Validated @RequestBody CategoryRequestDTO categoryRequestDTO) {
        CategoryCreateRequestDTO createDTO = CategoryCreateRequestDTO.builder()
                .name(categoryRequestDTO.getName())
                .build();
        CategoryServiceResponseDTO serviceResponse = categoryService.createCategory(createDTO);
        CategoryResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    public ResponseEntity<CategoryResponseDTO> getCategoryById(@PathVariable("id") Long categoryId) {
        CategoryServiceResponseDTO serviceResponse = categoryService.getCategoryById(categoryId);
        CategoryResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping
    public ResponseEntity<List<CategoryResponseDTO>> getAllCategories() {
        List<CategoryServiceResponseDTO> serviceResponses = categoryService.getAllCategories();
        List<CategoryResponseDTO> responseDTOs = serviceResponses.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responseDTOs);
    }

    @PutMapping("/{id}")
    public ResponseEntity<CategoryResponseDTO> updateCategory(
            @PathVariable("id") Long categoryId,
            @Validated @RequestBody CategoryRequestDTO categoryRequestDTO) {
        CategoryUpdateRequestDTO updateDTO = CategoryUpdateRequestDTO.builder()
                .name(categoryRequestDTO.getName())
                .build();
        CategoryServiceResponseDTO serviceResponse = categoryService.updateCategory(categoryId, updateDTO);
        CategoryResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCategory(@PathVariable("id") Long categoryId) {
        categoryService.deleteCategory(categoryId);
        return ResponseEntity.noContent().build();
    }

    // 카테고리 내 Aspect CRUD
    @PostMapping("/{categoryId}/aspects")
    public ResponseEntity<CategoryAspectResponseDTO> createAspect(
            @PathVariable("categoryId") Long categoryId,
            @Validated @RequestBody CategoryAspectRequestDTO aspectRequestDTO) {
        CategoryAspectCreateRequestDTO createDTO = CategoryAspectCreateRequestDTO.builder()
                .aspect(aspectRequestDTO.getAspect())
                .build();
        CategoryAspectServiceResponseDTO serviceResponse = categoryAspectService.createAspect(categoryId, createDTO);
        CategoryAspectResponseDTO responseDTO = mapToAspectResponseDTO(serviceResponse);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping("/{categoryId}/aspects")
    public ResponseEntity<List<CategoryAspectResponseDTO>> getAllAspectsByCategory(@PathVariable("categoryId") Long categoryId) {
        List<CategoryAspectServiceResponseDTO> serviceResponses = categoryAspectService.getAllAspectsByCategory(categoryId);
        List<CategoryAspectResponseDTO> responseDTOs = serviceResponses.stream()
                .map(this::mapToAspectResponseDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/aspects/{id}")
    public ResponseEntity<CategoryAspectResponseDTO> getAspectById(@PathVariable("id") Long aspectId) {
        CategoryAspectServiceResponseDTO serviceResponse = categoryAspectService.getAspectById(aspectId);
        CategoryAspectResponseDTO responseDTO = mapToAspectResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/aspects/{id}")
    public ResponseEntity<CategoryAspectResponseDTO> updateAspect(
            @PathVariable("id") Long aspectId,
            @Validated @RequestBody CategoryAspectRequestDTO aspectRequestDTO) {
        CategoryAspectUpdateRequestDTO updateDTO = CategoryAspectUpdateRequestDTO.builder()
                .aspect(aspectRequestDTO.getAspect())
                .build();
        CategoryAspectServiceResponseDTO serviceResponse = categoryAspectService.updateAspect(aspectId, updateDTO);
        CategoryAspectResponseDTO responseDTO = mapToAspectResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @DeleteMapping("/aspects/{id}")
    public ResponseEntity<Void> deleteAspect(@PathVariable("id") Long aspectId) {
        categoryAspectService.deleteAspect(aspectId);
        return ResponseEntity.noContent().build();
    }

    // DTO 매핑 메서드

    private CategoryResponseDTO mapToResponseDTO(CategoryServiceResponseDTO serviceResponse) {
        return CategoryResponseDTO.builder()
                .categoryId(serviceResponse.getCategoryId())
                .name(serviceResponse.getName())
                .createdAt(serviceResponse.getCreatedAt())
                .updatedAt(serviceResponse.getUpdatedAt())
                .aspects(
                        serviceResponse.getAspects().stream()
                                .map(this::mapToAspectResponseDTO)
                                .collect(Collectors.toList())
                )
                .build();
    }

    private CategoryAspectResponseDTO mapToAspectResponseDTO(CategoryAspectServiceResponseDTO serviceResponse) {
        return CategoryAspectResponseDTO.builder()
                .id(serviceResponse.getId())
                .aspect(serviceResponse.getAspect())
                .build();
    }

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<String> handleResourceNotFound(ResourceNotFoundException ex){
        return new ResponseEntity<>(ex.getMessage(), HttpStatus.NOT_FOUND);
    }

}