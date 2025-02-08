package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.UserCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.UserServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.UserUpdateRequestDTO;

import java.util.List;

public interface UserService {
    UserServiceResponseDTO createUser(UserCreateRequestDTO userCreateRequestDTO);
    UserServiceResponseDTO getUserById(Long userId);
    List<UserServiceResponseDTO> getAllUsers();
    UserServiceResponseDTO updateUser(Long userId, UserUpdateRequestDTO userUpdateRequestDTO);
    void deleteUser(Long userId);
}