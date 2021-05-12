<?php
#Sectors i els seus adjacents. Ordenar els sectors adjacents per aproximació
$neighbors = array("1" => array(2), "2"=>array(1,3,4),"3"=>array(4,5),"4"=>array(3,5,6),"5"=>array(4,6),"6"=>array(4,5,7),"7"=>array(6,5));
function Acces()
{
    $inicial = '192.168.1.10';
    $final = '192.168.1.254';
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
function llamada($ipadd, $user, $local)
{
    $host = "$ipadd";
    $port = 5678;
    $timeout = 3;
    $socket = @fsockopen( $host, 5678, $errno, $errstr, $timeout );
    $online = ( $socket !== false );
    if ($online){
        $f = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        socket_set_option($f, SOL_SOCKET, SO_SNDTIMEO, array('sec' => 1, 'usec' => 500000));
        $s = socket_connect($f, $host, $port);
        $msg = "##ALERTA DE POSSIBLE AGRESSIÓ##\n" . "Nombre: " . $user . "\n" . "Localización: " .$local;
        $len = strlen($msg);
        socket_sendto($f, $msg, $len, 0, $host, $port);
        socket_close($f);
        return true;
    } else {
        return false;
    }
}
$server = "127.0.0.1";
$us = "root";
$pass = "ascuan12";
$dbname = "alerta_agressio";
if(!empty($_GET) && Acces()) {
    $ipOrigen = $_SERVER["REMOTE_ADDR"];
    $server = "127.0.0.1";
    $us = "root";
    $pass = "ascuan12";
    $dbname = "alerta_agressio";
    $conn = new mysqli($server, $us, $pass, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    if(isset($_GET["hostname"])){
        $hostname = test_input($_GET["hostname"]);
    }
    if(isset($_GET["user"])){
        $user = test_input($_GET["user"]);
    }
    if(isset($_GET["uid"])){
        $uid = test_input($_GET["uid"]);
    }
    #Dos situacions: cridada i inserció en la base de dades
    if(isset($uid) && !isset($hostname)){
        $insertSQL = "INSERT INTO uids(uid, id_usuari) VALUES ($uid, $user)";
        $result = $conn->query($insertSQL);
        if(!$result){
            $text = date('d-m-Y H:i:s') . "Ja existeix un usuari amb aquesta uid: " . $user . " <---> " . $uid . PHP_EOL ;
            $writer = fopen("/php_logs/acces_denied.log", "w");
            fwrite($writer, $text);
            fclose($writer);
            exit;
        }

    }
    $ipOrigen = $_SERVER["REMOTE_ADDR"];

    $conn = new mysqli($server, $us, $pass, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    #Comproba l'adreça el cual ha enviat la sol·licitud HTTP
    $checkSQL = "SELECT hostname FROM ordinador WHERE ip LIKE '%$ipOrigen%' AND hostname LIKE '%$hostname%'";
    $check = $conn->query($checkSQL);
    $filename = '/php_logs/acces_denied.txt';
    if($check->num_rows == 0){
        $text = date('d-m-Y H:i:s') . " ==> Error de concordança entre IP i Hostname: " . $ipOrigen . " <---> " . $hostname ."\n";
        $handle = fopen($filename, 'a');
        fwrite($handle, $text);
        fclose($handle);
        exit;
    }
    #Comproba la UID de l'usuari.
    $uidSQL = "SELECT user FROM uids WHERE uid LIKE '$uid' AND user LIKE '$user'";
    $uidCheck = $conn->query($uidSQL);
    if($uidCheck->num_rows == 0){
        $text = date('d-m-Y H:i:s') . " ==> Error de concordança entre UID i nom d'usuari: " . $uid . " <---> " . $user . " ---- IP: ". $ipOrigen ."\n";
        $handle = fopen($filename, 'a');
        fwrite($handle, $text);
        fclose($handle);
        exit;
    }
    #Registra l'alerta
    $text = date('d-m-Y H:i:s') . "Usuari: " . $user . " #---# Hostname:  " . $hostname . "#---# IP: " . $ipOrigen  ."\n";
    $handle = fopen("/php_logs/alertes.txt", 'a');
    fwrite($handle, $text);
    fclose($handle);
    $searchSQL = "SELECT o.ip, u.nom FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id 
                                                  AND u.sector IN (SELECT sector FROM ubicacio uu, ordinador oo 
                                                  WHERE uu.id = oo.id_ubicacio AND oo.hostname LIKE '$hostname') 
                                                  AND hostname NOT LIKE '$hostname'";
    $result = $conn->query($searchSQL);
   if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $off = 0;
            $ip = $row["ip"];
            $lo = $row["nom"];
            if(!llamada($ip,$user,$lo)){
                $off++;
            }
        }
    }
    $sectorsSQL = "SELECT count(*) AS total FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id AND u.sector IN (SELECT uu.sector FROM ordinador oo, ubicacio uu WHERE oo.id_ubicacio = uu.id AND oo.hostname LIKE '$hostname') GROUP BY u.sector";
    $count = $conn->query($sectorsSQL)->fetch_assoc();
    $sectors = (int)$count["total"];
    if( $off > $sectors / 2 ){
        $neighbor = $conn->query("SELECT u.sector AS total FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id AND o.hostname LIKE '$hostname'")->fetch_assoc();
        $count = count($neighbors[$neighbor]);
        for ($x = 0;$x >= $count; $x++ ){
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
                if($contador < $result->num_rows() / 2){
                    break;
                }
            }
        }

} else {
    echo "Accés denegat";
}
?>
