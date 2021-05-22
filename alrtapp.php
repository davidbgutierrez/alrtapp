<?php
#Sectors i els seus adjacents. Ordenar els sectors adjacents per aproximació
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
function llamada($ipadd, $username, $local)
{
    $host = $ipadd;
    var_dump($host);
    $port = 5555;
    $timeout = 1;
    $socket = @fsockopen( $host, $port, $errno, $errstr, $timeout );
    $online = ( $socket !== false );
    if ($online){
        $f = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        socket_set_option($f, SOL_SOCKET, SO_SNDTIMEO, array('sec' => 1, 'usec' => 500000));
        $s = socket_connect($f, $host, $port);
        $msg = "Nom: " . $username . "\n" . "Localizatció: " .$local;
        /*$msg = "Nom: David Bartolomé Gutiérrez Cladera \n Localització: Consulta 24"; */
        $len = strlen($msg);
        socket_sendto($f, $msg, $len, 0, $host, $port);
        socket_close($f);
        return true;
    } else {
        return false;
    }
}
if(!empty($_GET) && Acces()) {
    $ipOrigen = $_SERVER["REMOTE_ADDR"];
    $server = "127.0.0.1";
    $us = "root";
    $pass = "ascuan12";
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
    #Dos situacions: cridada i inserció en la base de dades
    if(isset($uid) && !isset($hostname)){
        $insertSQL = "INSERT INTO uid(uid, user) VALUES ('$uid', '$user')";
        $result = $conn->query($insertSQL);
        var_dump($result);
        if(!$result){
            $text = date('d-m-Y H:i:s') . " Ja existeix un usuari amb aquesta uid: " . $user . " <---> " . $uid . PHP_EOL ;
            $writer = fopen("/php_logs/acces_denied.txt", "w");
            fwrite($writer, $text);
            fclose($writer);
            exit;
        }

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
    $uidSQL = "SELECT user FROM uid WHERE uid LIKE '$uid' AND user LIKE '$user'";
    $uidCheck = $conn->query($uidSQL);
    if($uidCheck->num_rows == 0){
        $text = date('d-m-Y H:i:s') . " ==> Error de concordança entre UID i nom d'usuari: " . $uid . " <---> " . $user . " ---- IP: ". $ipOrigen ."\n";
        $handle = fopen($filename, 'a');
        fwrite($handle, $text);
        fclose($handle);
        exit;
    }
    #Insereix l'alerta a la base de dades.
    $registreSQL = "INSERT INTO registre(id_usuari,hostname,ip,fecha) VALUES ('$user', '$hostname', '$ipOrigen', now())";
    $query = $conn->query($registreSQL);
    #Treu en quina ubicació es troba i el nom complet de l'usuari.
    $consulta = "SELECT u.nom, concat(us.nom, ' ', us.cognoms) as fullname FROM ordinador o, ubicacio u, usuari us WHERE o.id_ubicacio = u.id AND o.hostname LIKE '$hostname' AND us.id LIKE '$user'";
    $localArray = $conn->query($consulta)->fetch_assoc();
    $lo = $localArray["nom"];
    $nom = $localArray["fullname"];
    $searchSQL = "SELECT o.ip  FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id
                                                  AND u.sector IN (SELECT sector FROM ubicacio uu, ordinador oo
                                                  WHERE uu.id = oo.id_ubicacio AND oo.hostname LIKE '$hostname')
                                                  AND o.hostname NOT LIKE '$hostname'";
    $result = $conn->query($searchSQL);
   if ($result->num_rows > 0) {
    $off = 0;
        while ($row = $result->fetch_assoc()) {
            $ip = $row["ip"];
         if(!llamada($ip,$nom,$lo)){
                $off++;
            }
        }
    }
#En cas de que hagi més de la meitat dels equips del sector que no li arriba la notificiació, s'extenderà la cridada a sectors adjancents.
 $sectorsSQL = "SELECT count(*) AS total FROM ordinador o, ubicacio u WHERE o.id_ubicacio = u.id AND u.sector IN (SELECT uu.sector FROM ordinador oo, ubicacio uu WHERE oo.id_ubicacio = uu.id AND oo.hostname LIKE '$hostname') GROUP BY u.sector";
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
                    break;
                }
            }
        }
} else {
    echo "Accés denegat";
}
?>
