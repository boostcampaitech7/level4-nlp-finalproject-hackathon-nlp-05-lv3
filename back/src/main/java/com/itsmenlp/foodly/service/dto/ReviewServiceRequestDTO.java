package com.itsmenlp.foodly.service.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewServiceRequestDTO {

    private Integer rate;
    private String comment;
}