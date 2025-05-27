
<?php
$host = "dpg-d0npiqqli9vc73882atg-a";
$db = "gtweb_db";
$user = "gtweb_db_user";
$pass = "pjL83uSyzTTzifF79ZYuSGmomiXlGPwp";
$port = "5432";

// Connexion PostgreSQL avec PDO
try {
    $conn = new PDO("pgsql:host=$host;port=$port;dbname=$db", $user, $pass);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // echo "Connexion réussie à la base de données Render.";
} catch (PDOException $e) {
    echo "Erreur de connexion : " . $e->getMessage();
    exit;
}
?>
