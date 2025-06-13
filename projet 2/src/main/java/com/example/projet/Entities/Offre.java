package com.example.projet.Entities;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDate;
import java.util.List;


@Entity
@Getter
@Setter
@NoArgsConstructor
public class Offre {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @JsonProperty("title")
    private String titre;

    private String department;

    private String description;

    @JsonProperty("location")
    private String localisation;

    @JsonProperty("salaryRange")
    private String salaryRange;

    private String status; // open or closed

    @ElementCollection
    private List<String> requirements;

    @JsonProperty("typeContrat")
    private String typeContrat; // CDI, CDD, Stage

    @JsonProperty("postedDate")
    private LocalDate datePublication;

    @JsonProperty("attachmentUrl")
    private String fichierJointPath; // pour le PDF

}
