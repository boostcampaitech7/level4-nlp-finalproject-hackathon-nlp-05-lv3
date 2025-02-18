package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.service.dto.CartServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.CartServiceResponseDTO;

import java.util.List;

public interface CartService {

    CartServiceResponseDTO addProductToCart(Long userId, CartServiceRequestDTO requestDTO);

    List<CartServiceResponseDTO> getAllCartItems(Long userId);

    CartServiceResponseDTO getCartItemById(Long userId, Long cartId);

    CartServiceResponseDTO updateCartItem(Long userId, Long cartId, CartServiceRequestDTO requestDTO);

    void removeCartItem(Long userId, Long cartId);
}