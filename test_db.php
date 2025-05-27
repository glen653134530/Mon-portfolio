
<?php
require_once 'db_config.php';

try {
    $stmt = $conn->query("SELECT NOW()");
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    echo "Connexion réussie à la base de données Render !<br>";
    echo "Heure actuelle du serveur PostgreSQL : " . $row['now'];
} catch (PDOException $e) {
    echo "Erreur lors de la requête : " . $e->getMessage();
}
?>
