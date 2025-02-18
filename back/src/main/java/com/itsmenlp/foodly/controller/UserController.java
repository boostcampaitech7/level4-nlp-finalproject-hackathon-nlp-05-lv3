package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.UserRequestDTO;
import com.itsmenlp.foodly.controller.dto.UserResponseDTO;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.service.UserService;
import com.itsmenlp.foodly.service.dto.UserCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.UserServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.UserUpdateRequestDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user")
public class UserController {

    private final UserService userService;

    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping
    public ResponseEntity<UserResponseDTO> createUser(@Validated @RequestBody UserRequestDTO userRequestDTO) {
        UserCreateRequestDTO createDTO = UserCreateRequestDTO.builder()
                .email(userRequestDTO.getEmail())
                .username(userRequestDTO.getUsername())
                .build();
        UserServiceResponseDTO serviceResponse = userService.createUser(createDTO);
        UserResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponseDTO> getUserById(@PathVariable("id") Long userId) {
        UserServiceResponseDTO serviceResponse = userService.getUserById(userId);
        UserResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping
    public ResponseEntity<List<UserResponseDTO>> getAllUsers() {
        List<UserServiceResponseDTO> serviceResponses = userService.getAllUsers();
        List<UserResponseDTO> responseDTOs = serviceResponses.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responseDTOs);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserResponseDTO> updateUser(
            @PathVariable("id") Long userId,
            @Validated @RequestBody UserRequestDTO userRequestDTO) {
        UserUpdateRequestDTO updateDTO = UserUpdateRequestDTO.builder()
                .username(userRequestDTO.getUsername())
                .build();
        UserServiceResponseDTO serviceResponse = userService.updateUser(userId, updateDTO);
        UserResponseDTO responseDTO = mapToResponseDTO(serviceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable("id") Long userId) {
        userService.deleteUser(userId);
        return ResponseEntity.noContent().build();
    }

    private UserResponseDTO mapToResponseDTO(UserServiceResponseDTO serviceResponse) {
        return UserResponseDTO.builder()
                .userId(serviceResponse.getUserId())
                .email(serviceResponse.getEmail())
                .username(serviceResponse.getUsername())
                .createdAt(serviceResponse.getCreatedAt())
                .updatedAt(serviceResponse.getUpdatedAt())
                .build();
    }

    // Exception Handler
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<String> handleResourceNotFound(ResourceNotFoundException ex){
        return new ResponseEntity<>(ex.getMessage(), HttpStatus.NOT_FOUND);
    }

}