package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.AddressServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.AddressServiceResponseDTO;

import java.util.List;

public interface AddressService {

    AddressServiceResponseDTO createAddress(Long userId, AddressServiceRequestDTO requestDTO);
    List<AddressServiceResponseDTO> getAllAddresses(Long userId);
    AddressServiceResponseDTO getAddressById(Long userId, Long addressId);
    AddressServiceResponseDTO updateAddress(Long userId, Long addressId, AddressServiceRequestDTO requestDTO);
    void deleteAddress(Long userId, Long addressId);
}