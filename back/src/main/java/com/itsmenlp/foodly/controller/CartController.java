package com.itsmenlp.foodly.controller;

import com.itsmenlp.foodly.controller.dto.CartRequestDTO;
import com.itsmenlp.foodly.controller.dto.CartResponseDTO;
import com.itsmenlp.foodly.service.CartService;
import com.itsmenlp.foodly.service.dto.CartServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.CartServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user/{userId}/cart")
@RequiredArgsConstructor
public class CartController {

    private final CartService cartService;

    /**
     * 장바구니 항목 추가
     * POST /api/user/{userId}/cart
     */
    @PostMapping
    public ResponseEntity<CartResponseDTO> addProductToCart(
            @PathVariable Long userId,
            @Valid @RequestBody CartRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        CartServiceRequestDTO serviceRequestDTO = CartServiceRequestDTO.builder()
                .productId(requestDTO.getProductId())
                .quantity(requestDTO.getQuantity())
                .build();

        CartServiceResponseDTO serviceResponseDTO = cartService.addProductToCart(userId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        CartResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    /**
     * 모든 장바구니 항목 조회
     * GET /api/user/{userId}/cart
     */
    @GetMapping
    public ResponseEntity<List<CartResponseDTO>> getAllCartItems(@PathVariable Long userId) {
        List<CartServiceResponseDTO> serviceResponseDTOs = cartService.getAllCartItems(userId);

        // Service DTO를 Controller DTO로 변환
        List<CartResponseDTO> responseDTOs = serviceResponseDTOs.stream()
                .map(this::mapToResponseDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responseDTOs);
    }

    /**
     * 특정 장바구니 항목 조회
     * GET /api/user/{userId}/cart/{cartId}
     */
    @GetMapping("/{cartId}")
    public ResponseEntity<CartResponseDTO> getCartItemById(
            @PathVariable Long userId,
            @PathVariable Long cartId) {

        CartServiceResponseDTO serviceResponseDTO = cartService.getCartItemById(userId, cartId);

        // Service DTO를 Controller DTO로 변환
        CartResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 장바구니 항목 업데이트
     * PUT /api/user/{userId}/cart/{cartId}
     */
    @PutMapping("/{cartId}")
    public ResponseEntity<CartResponseDTO> updateCartItem(
            @PathVariable Long userId,
            @PathVariable Long cartId,
            @Valid @RequestBody CartRequestDTO requestDTO) {

        // Controller DTO를 Service DTO로 변환
        CartServiceRequestDTO serviceRequestDTO = CartServiceRequestDTO.builder()
                .productId(requestDTO.getProductId())
                .quantity(requestDTO.getQuantity())
                .build();

        CartServiceResponseDTO serviceResponseDTO = cartService.updateCartItem(userId, cartId, serviceRequestDTO);

        // Service DTO를 Controller DTO로 변환
        CartResponseDTO responseDTO = mapToResponseDTO(serviceResponseDTO);

        return ResponseEntity.ok(responseDTO);
    }

    /**
     * 장바구니 항목 삭제
     * DELETE /api/user/{userId}/cart/{cartId}
     */
    @DeleteMapping("/{cartId}")
    public ResponseEntity<Void> deleteCartItem(
            @PathVariable Long userId,
            @PathVariable Long cartId) {

        cartService.removeCartItem(userId, cartId);
        return ResponseEntity.noContent().build();
    }

    private CartResponseDTO mapToResponseDTO(CartServiceResponseDTO serviceResponseDTO) {
        return CartResponseDTO.builder()
                .cartId(serviceResponseDTO.getCartId())
                .userId(serviceResponseDTO.getUserId())
                .productId(serviceResponseDTO.getProductId())
                .productName(serviceResponseDTO.getProductName())
                .quantity(serviceResponseDTO.getQuantity())
                .addedAt(serviceResponseDTO.getAddedAt())
                .build();
    }
}