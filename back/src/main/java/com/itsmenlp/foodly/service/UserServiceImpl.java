package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.User;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.UserRepository;
import com.itsmenlp.foodly.service.dto.UserCreateRequestDTO;
import com.itsmenlp.foodly.service.dto.UserServiceResponseDTO;
import com.itsmenlp.foodly.service.dto.UserUpdateRequestDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;

    @Autowired
    public UserServiceImpl(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserServiceResponseDTO createUser(UserCreateRequestDTO dto) {
        User user = User.builder()
                .email(dto.getEmail())
                .username(dto.getUsername())
                .build();
        User savedUser = userRepository.save(user);
        return mapToResponseDTO(savedUser);
    }

    @Override
    @Transactional(readOnly = true)
    public UserServiceResponseDTO getUserById(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id " + userId));
        return mapToResponseDTO(user);
    }

    @Override
    @Transactional(readOnly = true)
    public List<UserServiceResponseDTO> getAllUsers() {
        List<User> users = userRepository.findAll();
        return users.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    public UserServiceResponseDTO updateUser(Long userId, UserUpdateRequestDTO dto) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id " + userId));
        user.setUsername(dto.getUsername());
        User updatedUser = userRepository.save(user);
        return mapToResponseDTO(updatedUser);
    }

    @Override
    public void deleteUser(Long userId) {
        if(!userRepository.existsById(userId)) {
            throw new ResourceNotFoundException("User not found with id " + userId);
        }
        userRepository.deleteById(userId);
    }

    private UserServiceResponseDTO mapToResponseDTO(User user) {
        return UserServiceResponseDTO.builder()
                .userId(user.getUserId())
                .email(user.getEmail())
                .username(user.getUsername())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}