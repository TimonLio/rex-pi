<?php

$context = new ZMQContext();

$reqs = new ZMQSocket($context, ZMQ::SOCKET_REQ);
$reqs->connect("tcp://localhost:5555");

$request = array();
$request['type'] = "WOL";
$request['macaddr'] = "AABBCCDDEEFF";

$reqs->send(json_encode($request));
$reply = $reqs->recv();
printf("Received reply: [%s]\n", $reply);

?>
