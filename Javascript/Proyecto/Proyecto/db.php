<?php

$conexion = mysqli_connect('localhost','root','','empleadosena') or die(mysql_error($mysqli));

insertar($conexion);

function insertar($conexion){
    $nombres=$_POST['nombres'];
    $apellidos=$_POST['apellidos'];
    $sexo=$_POST['sexo'];
    $nacimiento=$_POST['nacimiento'];
    $ingreso=$_POST['ingreso'];
    $salario=$_POST['salario'];
    $edad=$_POST['edad'];
    $antiguedad=$_POST['antiguedad'];
    $prestaciones=$_POST['prestaciones'];

    $consulta = "INSERT INTO empleados(nombres, apellidos, sexo, nacimiento, ingreso, salario, edad, antiguedad, prestaciones)
    VALUES ('$nombres', '$apellidos', '$sexo', '$nacimiento', '$ingreso', '$salario', '$edad', '$antiguedad', '$prestaciones')"; 
    mysqli_query($conexion, $consulta);
    echo "Sus datos se han guardado exitosamente!";
    mysqli_close($conexion);

    
} 


