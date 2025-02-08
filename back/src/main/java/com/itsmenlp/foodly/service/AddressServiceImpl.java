package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Address;
import com.itsmenlp.foodly.entity.User;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.AddressRepository;
import com.itsmenlp.foodly.repository.UserRepository;
import com.itsmenlp.foodly.service.dto.AddressServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.AddressServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AddressServiceImpl implements AddressService {

    private final AddressRepository addressRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional
    public AddressServiceResponseDTO createAddress(Long userId, AddressServiceRequestDTO requestDTO) {
        User user = getUserById(userId);

        Address address = Address.builder()
                .user(user)
                .address(requestDTO.getAddress())
                .build();

        Address savedAddress = addressRepository.save(address);

        return mapToServiceResponseDTO(savedAddress);
    }

    @Override
    @Transactional(readOnly = true)
    public List<AddressServiceResponseDTO> getAllAddresses(Long userId) {
        User user = getUserById(userId);
        List<Address> addresses = addressRepository.findByUser(user);

        return addresses.stream()
                .map(this::mapToServiceResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public AddressServiceResponseDTO getAddressById(Long userId, Long addressId) {
        User user = getUserById(userId);
        Address address = getAddressByIdAndUser(addressId, user);

        return mapToServiceResponseDTO(address);
    }

    @Override
    @Transactional
    public AddressServiceResponseDTO updateAddress(Long userId, Long addressId, AddressServiceRequestDTO requestDTO) {
        User user = getUserById(userId);
        Address address = getAddressByIdAndUser(addressId, user);

        address.setAddress(requestDTO.getAddress());

        Address updatedAddress = addressRepository.save(address);

        return mapToServiceResponseDTO(updatedAddress);
    }

    @Override
    @Transactional
    public void deleteAddress(Long userId, Long addressId) {
        User user = getUserById(userId);
        Address address = getAddressByIdAndUser(addressId, user);

        addressRepository.delete(address);
    }

    private User getUserById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
    }

    private Address getAddressByIdAndUser(Long addressId, User user) {
        return addressRepository.findById(addressId)
                .filter(address -> address.getUser().equals(user))
                .orElseThrow(() -> new ResourceNotFoundException("Address not found with id: " + addressId + " for user id: " + user.getUserId()));
    }

    private AddressServiceResponseDTO mapToServiceResponseDTO(Address address) {
        return AddressServiceResponseDTO.builder()
                .addressId(address.getAddressId())
                .userId(address.getUser().getUserId())
                .address(address.getAddress())
                .createdAt(address.getCreatedAt())
                .updatedAt(address.getUpdatedAt())
                .build();
    }
}