package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.AddressRequestDTO;
import com.itsmenlp.foodly.controller.dto.AddressResponseDTO;
import com.itsmenlp.foodly.service.AddressService;
import com.itsmenlp.foodly.service.dto.AddressServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.AddressServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user/{userId}/address")
@RequiredArgsConstructor
public class AddressController {

    private final AddressService addressService;

    /**
     * 주소 생성
     * POST /api/user/{userId}/address
     */
    @PostMapping
    public ResponseEntity<AddressResponseDTO> createAddress(
            @PathVariable Long userId,
            @Valid @RequestBody AddressRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        AddressServiceRequestDTO serviceRequestDTO = AddressServiceRequestDTO.builder()
                .address(requestDTO.getAddress())
                .build();

        AddressServiceResponseDTO serviceResponseDTO = addressService.createAddress(userId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        AddressResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    /**
     * 모든 주소 조회
     * GET /api/user/{userId}/address
     */
    @GetMapping
    public ResponseEntity<List<AddressResponseDTO>> getAllAddresses(@PathVariable Long userId) {
        List<AddressServiceResponseDTO> serviceResponseDTOs = addressService.getAllAddresses(userId);

        // Service DTO를 Controller DTO로 변환
        List<AddressResponseDTO> responseDTOs = serviceResponseDTOs.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responseDTOs);
    }

    /**
     * 특정 주소 조회
     * GET /api/user/{userId}/address/{addressId}
     */
    @GetMapping("/{addressId}")
    public ResponseEntity<AddressResponseDTO> getAddressById(
            @PathVariable Long userId,
            @PathVariable Long addressId) {

        AddressServiceResponseDTO serviceResponseDTO = addressService.getAddressById(userId, addressId);

        // Service DTO를 Controller DTO로 변환
        AddressResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 주소 업데이트
     * PUT /api/user/{userId}/address/{addressId}
     */
    @PutMapping("/{addressId}")
    public ResponseEntity<AddressResponseDTO> updateAddress(
            @PathVariable Long userId,
            @PathVariable Long addressId,
            @Valid @RequestBody AddressRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        AddressServiceRequestDTO serviceRequestDTO = AddressServiceRequestDTO.builder()
                .address(requestDTO.getAddress())
                .build();

        AddressServiceResponseDTO serviceResponseDTO = addressService.updateAddress(userId, addressId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        AddressResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 주소 삭제
     * DELETE /api/user/{userId}/address/{addressId}
     */
    @DeleteMapping("/{addressId}")
    public ResponseEntity<Void> deleteAddress(
            @PathVariable Long userId,
            @PathVariable Long addressId) {

        addressService.deleteAddress(userId, addressId);
        return ResponseEntity.noContent().build();
    }

    private AddressResponseDTO mapToResponseDTO(AddressServiceResponseDTO serviceResponseDTO) {
        return AddressResponseDTO.builder()
                .addressId(serviceResponseDTO.getAddressId())
                .userId(serviceResponseDTO.getUserId())
                .address(serviceResponseDTO.getAddress())
                .createdAt(serviceResponseDTO.getCreatedAt())
                .updatedAt(serviceResponseDTO.getUpdatedAt())
                .build();
    }
}