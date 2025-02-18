package com.itsmenlp.foodly.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Entity
@Table(name = "image_to_text")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ImageToText {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 입력 데이터
    private String link;

    @ElementCollection
    @CollectionTable(joinColumns = @JoinColumn(name = "image_to_text_id"))
    @Column(name = "image_url")
    private List<String> inputImages;

    // 외부 API에서 반환받은 결과
    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(joinColumns = @JoinColumn(name = "image_to_text_id"))
    @Column(name = "text", columnDefinition = "TEXT")
    private List<String> outputTexts;
}