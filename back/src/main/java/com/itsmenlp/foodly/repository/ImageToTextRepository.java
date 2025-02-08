package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.ImageToText;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ImageToTextRepository extends JpaRepository<ImageToText, Long> {
}