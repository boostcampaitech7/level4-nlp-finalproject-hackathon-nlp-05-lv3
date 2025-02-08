package com.itsmenlp.foodly.service;

import com.itsmenlp.foodly.entity.Cart;
import com.itsmenlp.foodly.entity.Product;
import com.itsmenlp.foodly.entity.User;
import com.itsmenlp.foodly.exception.ResourceNotFoundException;
import com.itsmenlp.foodly.repository.CartRepository;
import com.itsmenlp.foodly.repository.ProductRepository;
import com.itsmenlp.foodly.repository.UserRepository;
import com.itsmenlp.foodly.service.dto.CartServiceRequestDTO;
import com.itsmenlp.foodly.service.dto.CartServiceResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CartServiceImpl implements CartService {

    private final CartRepository cartRepository;
    private final UserRepository userRepository;
    private final ProductRepository productRepository;

    @Override
    @Transactional
    public CartServiceResponseDTO addProductToCart(Long userId, CartServiceRequestDTO requestDTO) {
        User user = getUserById(userId);
        Product product = getProductById(requestDTO.getProductId());

        // 유저의 장바구니에 이미 해당 상품이 있는지 확인
        boolean exists = cartRepository.existsByProductAndUser(product, user);
        if (exists) {
            throw new IllegalArgumentException("Product already exists in the cart.");
        }

        Cart cart = Cart.builder()
                .user(user)
                .product(product)
                .quantity(requestDTO.getQuantity())
                .build();

        Cart savedCart = cartRepository.save(cart);

        return mapToServiceResponseDTO(savedCart);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CartServiceResponseDTO> getAllCartItems(Long userId) {
        User user = getUserById(userId);
        List<Cart> carts = cartRepository.findByUser(user);

        return carts.stream()
                .map(this::mapToServiceResponseDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public CartServiceResponseDTO getCartItemById(Long userId, Long cartId) {
        User user = getUserById(userId);
        Cart cart = getCartByIdAndUser(cartId, user);

        return mapToServiceResponseDTO(cart);
    }

    @Override
    @Transactional
    public CartServiceResponseDTO updateCartItem(Long userId, Long cartId, CartServiceRequestDTO requestDTO) {
        User user = getUserById(userId);
        Cart cart = getCartByIdAndUser(cartId, user);

        // 업데이트할 상품이 다른 상품일 경우 중복 확인
        if (!cart.getProduct().getProductId().equals(requestDTO.getProductId())) {
            Product newProduct = getProductById(requestDTO.getProductId());
            boolean exists = cartRepository.existsByProductAndUser(newProduct, user);
            if (exists) {
                throw new IllegalArgumentException("Product already exists in the cart.");
            }
            cart.setProduct(newProduct);
        }

        cart.setQuantity(requestDTO.getQuantity());

        Cart updatedCart = cartRepository.save(cart);

        return mapToServiceResponseDTO(updatedCart);
    }

    @Override
    @Transactional
    public void removeCartItem(Long userId, Long cartId) {
        User user = getUserById(userId);
        Cart cart = getCartByIdAndUser(cartId, user);

        cartRepository.delete(cart);
    }

    private User getUserById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
    }

    private Product getProductById(Long productId) {
        return productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + productId));
    }

    private Cart getCartByIdAndUser(Long cartId, User user) {
        return cartRepository.findByCartIdAndUser(cartId, user)
                .orElseThrow(() -> new ResourceNotFoundException("Cart not found with id: " + cartId + " for user id: " + user.getUserId()));
    }

    private CartServiceResponseDTO mapToServiceResponseDTO(Cart cart) {
        return CartServiceResponseDTO.builder()
                .cartId(cart.getCartId())
                .userId(cart.getUser().getUserId())
                .productId(cart.getProduct().getProductId())
                .productName(cart.getProduct().getName())
                .quantity(cart.getQuantity())
                .addedAt(cart.getAddedAt())
                .build();
    }
}