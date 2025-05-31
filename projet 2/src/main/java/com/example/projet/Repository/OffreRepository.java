package com.example.projet.Repository;

import com.example.projet.Entities.Offre;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

public interface OffreRepository extends JpaRepository<Offre, Long>{
}

