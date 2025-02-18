package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.Description;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DescriptionRepository extends JpaRepository<Description, Long> {

}