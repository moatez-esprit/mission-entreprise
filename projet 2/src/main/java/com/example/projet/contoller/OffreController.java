package com.example.projet.contoller;


import com.example.projet.Entities.Offre;
import com.example.projet.services.OffreService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;


import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/offres")
@CrossOrigin(origins = "*") // autorise toutes les origines, à adapter selon le besoin
public class OffreController {

    @Autowired
    private OffreService offreService;

    // ➕ Créer une nouvelle offre
    @PostMapping
    public ResponseEntity<Offre> ajouterOffre(@RequestBody Offre offre) {
        Offre nouvelleOffre = offreService.ajouter(offre);
        return ResponseEntity.ok(nouvelleOffre);
    }

    // 📄 Récupérer toutes les offres
    @GetMapping
    public ResponseEntity<List<Offre>> getToutesLesOffres() {
        return ResponseEntity.ok(offreService.getAll());
    }

    // 🔍 Récupérer une offre par ID
    @GetMapping("/{id}")
    public ResponseEntity<Offre> getOffreById(@PathVariable Long id) {
        return ResponseEntity.ok(offreService.getById(id));
    }

    // ✏️ Modifier une offre
    @PutMapping("/{id}")
    public ResponseEntity<Offre> modifierOffre(@PathVariable Long id, @RequestBody Offre offre) {
        Offre maj = offreService.modifier(id, offre);
        return ResponseEntity.ok(maj);
    }

    // ❌ Supprimer une offre
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> supprimerOffre(@PathVariable Long id) {
        offreService.supprimer(id);
        return ResponseEntity.noContent().build();
    }

    // 📎 Upload d'un fichier (PDF)
    @PostMapping("/{id}/upload")
    public ResponseEntity<String> uploadFichier(@PathVariable Long id, @RequestParam("file") MultipartFile file) {
        try {
            String chemin = offreService.uploadFichier(id, file);
            return ResponseEntity.ok("Fichier enregistré : " + chemin);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Erreur upload : " + e.getMessage());
        }
    }
}
