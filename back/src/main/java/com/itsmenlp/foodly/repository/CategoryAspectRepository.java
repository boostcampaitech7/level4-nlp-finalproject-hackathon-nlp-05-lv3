package com.itsmenlp.foodly.repository;

import com.itsmenlp.foodly.entity.CategoryAspect;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CategoryAspectRepository extends JpaRepository<CategoryAspect, Long> {

}