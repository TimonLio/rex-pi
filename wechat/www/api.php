<?php

/**
 * Define config table
 * $config['debug']         = false;
 * $config['wechat_token']  = "TOKEN";
 */
require_once("inc/config.php");

if (isset($_GET['echostr'])) {
    $echoStr = $_GET['echostr'];

    if (checkSignature()) {
	echo $echoStr;
    } else {
	echo "Failed";
    }
    exit;
} else {
    //get post data, May be due to the different environments
    //$postStr = $_POST['HTTP_RAW_POST_DATA'];
    $postStr = isset($GLOBALS["HTTP_RAW_POST_DATA"]) ? $GLOBALS["HTTP_RAW_POST_DATA"] : null;

    //extract post data
    if (!empty($postStr)) {
	/*
	 * libxml_disable_entity_loader is to prevent XML eXternal Entity Injection,
	 * the best way is to check the validity of xml by yourself
	 */
	libxml_disable_entity_loader(true);
	$postObj = simplexml_load_string($postStr, 'SimpleXMLElement', LIBXML_NOCDATA);
	$msgId = $postObj->MsgId;
	$msgType = $postObj->MsgType;
	$fromUserName = $postObj->FromUserName;
	$toUserName = $postObj->ToUserName;
	$createTime = $postObj->CreateTime;
	$content = trim($postObj->Content);

	handleMessage($toUserName, $fromUserName, $createTime, $msgType, $content, $msgId);
    }
}

function checkSignature()
{
    global $config;

    if (!isset($config['wechat_token'])) {
	throw new Exception('TOKEN not defined!');
    }
    $token = $config['wechat_token'];

    $signature = isset($_GET['signature']) ? trim($_GET['signature']) : "";
    $timestamp = isset($_GET['timestamp']) ? trim($_GET['timestamp']) : "";
    $nonce = isset($_GET['nonce']) ? trim($_GET['nonce']) : "";

    $tmpArr = array($token, $timestamp, $nonce);
    sort($tmpArr, SORT_STRING); // use SORT_STRING rule
    $tmpStr = implode($tmpArr);
    $tmpStr = sha1($tmpStr);

    return ($tmpStr == $signature);
}

function handleMessage($toUserName, $fromUserName, $createTime, $msgType, $content, $msgId)
{
    $contentStr = strtolower(trim($content));
    if (0 == stripos($contentStr, "wol")) {
	$arr = explode("_", $contentStr);
	$macaddr = $arr[count($arr) - 1];
	if (ereg("[0-9a-f]{12}", $macaddr)) {
	    handleWakeOnLan($macaddr);
	    printResponse($fromUserName, $toUserName, "Magic sent");
	} else {
	    printResponse($fromUserName, $toUserName, "Mac address ${macaddr} invalid");
	}
    } else if ($contentStr == "func2") {
	printResponse($fromUserName, $toUserName, "Response for func2");
    } else {
	printResponse($fromUserName, $toUserName,
		"Unknown message [${contentStr}]!");
    }
}

function handleWakeOnLan($macaddr)
{
    $context = new ZMQContext();

    $reqs = new ZMQSocket($context, ZMQ::SOCKET_REQ);
    $reqs->connect("tcp://localhost:5555");

    $request = array();
    $request['type'] = "WOL";
    $request['macaddr'] = $macaddr;

    $reqs->send(json_encode($request));
    $reply = $reqs->recv();
    printf("Received reply: [%s]\n", $reply);
}

function printResponse($toUserName, $fromUserName, $content)
{
    $createTime = time();
    $msgType = "text";
    $textTpl = "<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[%s]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>";
    if (!empty($content)) {
	printf($textTpl, $toUserName, $fromUserName, $createTime, $msgType, $content);
    } else {
	echo "Input something...";
    }
}

/* vim:et:ts=4:sw=4: */
?>
