package com.example.projet.services;


import com.example.projet.Entities.Offre;
import com.example.projet.Repository.OffreRepository;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.util.List;

@Service
public class OffreService {

    private final String UPLOAD_DIR = "uploads/";

    @Autowired
    private OffreRepository offreRepository;

    // ➕ Ajouter une nouvelle offre
    public Offre ajouter(Offre offre) {
        offre.setDatePublication(LocalDate.now());
        return offreRepository.save(offre);
    }

    // 📄 Liste de toutes les offres
    public List<Offre> getAll() {
        return offreRepository.findAll();
    }

    // 🔍 Récupérer une offre par ID
    public Offre getById(Long id) {
        return offreRepository.findById(id).orElseThrow(() -> new RuntimeException("Offre non trouvée"));
    }

    // ✏️ Modifier une offre existante
    public Offre modifier(Long id, Offre updatedOffre) {
        Offre existing = getById(id);
        existing.setTitre(updatedOffre.getTitre());
        existing.setDepartment(updatedOffre.getDepartment());
        existing.setDescription(updatedOffre.getDescription());
        existing.setLocalisation(updatedOffre.getLocalisation());
        existing.setSalaryRange(updatedOffre.getSalaryRange());
        existing.setStatus(updatedOffre.getStatus());
        existing.setRequirements(updatedOffre.getRequirements());
        existing.setTypeContrat(updatedOffre.getTypeContrat());
        return offreRepository.save(existing);
    }

    // ❌ Supprimer une offre
    public void supprimer(Long id) {
        offreRepository.deleteById(id);
    }

    // 📎 Upload fichier joint (PDF)
    public String uploadFichier(Long offreId, MultipartFile file) throws IOException {
        Offre offre = getById(offreId);

        // Créer le dossier s'il n'existe pas
        Files.createDirectories(Paths.get(UPLOAD_DIR));

        String filename = file.getOriginalFilename();
        String cheminComplet = UPLOAD_DIR + System.currentTimeMillis() + "_" + filename;
        Path chemin = Paths.get(cheminComplet);

        // Sauvegarder le fichier
        Files.copy(file.getInputStream(), chemin, StandardCopyOption.REPLACE_EXISTING);

        // Enregistrer le chemin dans l'offre
        offre.setFichierJointPath(cheminComplet);
        offreRepository.save(offre);

        return cheminComplet;
    }
}
