<?php
$neighbors = array("1" => array(2), "2"=>array(1,3,4),"3"=>array(4,5),"4"=>array(3,5,6),"5"=>array(4,6),"6"=>array(4,5,7),"7"=>array(6,5));
function Acces()
{
    $inicial = '192.168.1.20';
    $final = '192.168.1.240';
    $ip = ip2long($_SERVER['REMOTE_ADDR']);
    return($ip >= ip2long($inicial) && $ip <= ip2long($final));
}
function test_input($data)
{
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}
function llamada($ipadd, $username, $local,$clau,$vi,$se)
{
    $ivint= (int)$vi;
    $host = $ipadd;
    $port = 5555;
    $timeout = 1;
    $socket = @fsockopen( $host, $port, $errno, $errstr, $timeout );
    $online = ( $socket !== false );
    if ($online){
        $f = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        socket_set_option($f, SOL_SOCKET, SO_SNDTIMEO, array('sec' => 1, 'usec' => 500000));
        $s = socket_connect($f, $host, $port);
	    $message = $se . "\n" . " Nom: " . $username . " \n " . "Localizatció: " .$local;
	    $cipher = "aes-256-cbc";
	    $ivlen = openssl_cipher_iv_length($cipher);
	    $ciphertext = openssl_encrypt($message, $cipher, $clau, $options=0, $ivint);
        $len = strlen($ciphertext);
        socket_sendto($f, $ciphertext, $len, 0, $host, $port);
        socket_close($f);
        return true;
    } else {
        return false;
    }
}
if(!empty($_GET) && Acces()) {
    $filename = '/php_logs/acces_denied.txt';
    $ipOrigen = $_SERVER["REMOTE_ADDR"];
    $server = "localhost";
    $us = "root";
    $pass = "Ascuan12?";
    $dbname = "alrtapp";
    $conn = new mysqli($server, $us, $pass, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    if(isset($_GET["hostname"])){
        $hostname = test_input($_GET["hostname"]);
    }
    if(isset($_GET["username"])){
        $user = test_input($_GET["username"]);
    }
    if(isset($_GET["uid"])){
        $uid = test_input($_GET["uid"]);
    }
    if(isset($_GET["secret"])){
        $secret = test_input($_GET["secret"]);
    }
    if(isset($_GET["key"])){
        $key = test_input($_GET["key"]);
    }
    if(isset($_GET["iv"])){
        $iv = test_input($_GET["iv"]);
    }
    if(isset($_GET["secret"])){
        $checkSQL = "SELECT * FROM ordinador WHERE `key` LIKE '$key' OR iv LIKE '$iv' OR secret LIKE '$secret' AND ip LIKE '$ipOrigen'";
        $check = $conn->query($checkSQL);
        if($check->num_rows == 0){
            $secretSQL = "UPDATE ordinador SET `key`='$key', iv='$iv', secret= '$secret' WHERE ip LIKE '$ipOrigen'";
            $result = $conn->query($secretSQL);
        } else{
            $text = date('d-m-Y H:i:s') . "S'ha intentat introduïr dades noves sense consentiment: ". $ipOrigen. PHP_EOL ;
            $writer = fopen("/php_logs/acces_denied.txt", "w");
            fwrite($writer, $text);
            fclose($writer);
        }
        $conn->close();
        exit;
    }
    if(isset($uid) && !isset($hostname)){
        $insertSQL = "INSERT INTO uid(uid, user) VALUES ('$uid', '$user')";
        $result = $conn->query($insertSQL);
        if(!$result){
            $text = date('d-m-Y H:i:s') . " Ja existeix un usuari amb aquesta uid: " . $user . " <---> " . $uid . PHP_EOL ;
            $writer = fopen("/php_logs/acces_denied.txt", "w");
            fwrite($writer, $text);
            fclose($writer);
            $conn->close();
        }
        exit;
    }
    $checkSQL = "SELECT hostname FROM ordinador WHERE ip LIKE '%$ipOrigen%' AND hostname LIKE '%$hostname%'";
    $check = $conn->query($checkSQL);
    if($check->num_rows == 0){
        $text = date('d-m-Y H:i:s') . " ==> Error de concordança entre IP i Hostname: " . $ipOrigen . " <---> " . $hostname ."\n";
        $handle = fopen($filename, 'a');
        fwrite($handle, $text);
        fclose($handle);
        $conn->close();
        exit;
    }
    $uidSQL = "SELECT user FROM uid WHERE uid LIKE '$uid' AND user LIKE '$user'";
    $uidCheck = $conn->query($uidSQL);
    if($uidCheck->num_rows == 0){
        $text = date('d-m-Y H:i:s') . " ==> Error de concordança entre UID i nom d'usuari: " . $uid . " <---> " . $user . " ---- IP: ". $ipOrigen ."\n";
        $handle = fopen($filename, 'a');
        fwrite($handle, $text);
        fclose($handle);
        $conn->close();
        exit;
    }
    $registreSQL = "INSERT INTO registre(id_usuari,hostname,ip,fecha) VALUES ('$user', '$hostname', '$ipOrigen', now())";
    $query = $conn->query($registreSQL);
    $consulta = "SELECT u.nom, concat(us.nom, ' ', us.cognoms) as fullname FROM ordinador o, ubicacio u, usuari us WHERE o.id_ubicacio = u.id AND o.hostname LIKE '$hostname' AND us.id LIKE '$user'";
    $localArray = $conn->query($consulta)->fetch_assoc();
    $lo = $localArray["nom"];
    $nom = $localArray["fullname"];
    $searchSQL = "SELECT o.ip, o.key, o.iv, o.secret  FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id
                                                  AND u.sector IN (SELECT sector FROM ubicacio uu, ordinador oo
                                                  WHERE uu.id = oo.id_ubicacio AND oo.hostname LIKE '$hostname')
                                                  AND o.hostname NOT LIKE '$hostname'";
    $result = $conn->query($searchSQL);
   if ($result->num_rows > 0) {
    $off = 0;
        while ($row = $result->fetch_assoc()) {
            $ip = $row["ip"];
            $key = $row["key"];
            $iv = $row["iv"];
            $secret = $row["secret"];
         if(!llamada($ip,$nom,$lo,$key,$iv,$secret)){
                $off++;
		echo "Offline: " . $ip . "<br/>";
            }else{ echo "Online: " . $ip . "<br/>";
}
        }
    }
/* $sectorsSQL = "SELECT count(*) AS total FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id AND u.sector IN (SELECT uu.sector FROM ordinador oo, ubicacio uu WHERE oo.id_ubicacio = uu.id AND oo.hostname LIKE '$hostname') GROUP BY u.sector";
 $count = $conn->query($sectorsSQL)->fetch_assoc();
 $sectors = (int)$count["total"];
   if( $off > $sectors / 2 ){
       $neighbor = $conn->query("SELECT u.sector AS total FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id AND o.hostname LIKE '$hostname'")->fetch_assoc();
       $count = count($neighbors[$neighbor]);
       for ($x = 0;$x <= $count; $x++ ){
           $sector = $neighbors[$neighbor][$x];
           $vecinos = "SELECT o.ip, u.nom FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id AND u.sector =  $sector";
           $result = $conn->query($vecinos);
               while ($row = $result->fetch_assoc()) {
                   $contador = 0;
                   $ip = $row["ip"];
                   $lo = $row["nom"];
                   if(!llamada($ip,$user,$lo)){
                       $contador++;
                   }
               }
               if($contador < $result->num_rows / 2){
                  $conn->close();
                  break;
               }
        }
    } else{
       $conn->close();
    }*/
} else {
    echo "Accés denegat";
}
?>
