<?php

/**
 * Define config table
 * $config['debug']         = false;
 * $config['wechat_token']  = "TOKEN";
 */
require_once("inc/config.php");

$wechatObj = new wechatCallbackapiTest();
$wechatObj->valid();

class wechatCallbackapiTest
{
    public function valid()
    {
        $echoStr = $_GET["echostr"];

        if ($this->checkSignature()) {
	    echo $echoStr;
	    exit;
	}
    }

    public function responseMsg()
    {
	//get post data, May be due to the different environments
	$postStr = $GLOBALS["HTTP_RAW_POST_DATA"];

      	//extract post data
	if (!empty($postStr)) {
	    /* libxml_disable_entity_loader is to prevent XML eXternal Entity Injection,
	       the best way is to check the validity of xml by yourself */
	    libxml_disable_entity_loader(true);
	    $postObj = simplexml_load_string($postStr, 'SimpleXMLElement', LIBXML_NOCDATA);
	    $fromUsername = $postObj->FromUserName;
	    $toUsername = $postObj->ToUserName;
	    $keyword = trim($postObj->Content);
	    $time = time();
	    $textTpl = "<xml>
		    <ToUserName><![CDATA[%s]]></ToUserName>
		    <FromUserName><![CDATA[%s]]></FromUserName>
		    <CreateTime>%s</CreateTime>
		    <MsgType><![CDATA[%s]]></MsgType>
		    <Content><![CDATA[%s]]></Content>
		    <FuncFlag>0</FuncFlag>
		    </xml>";             
	    if (!empty($keyword)) {
		$msgType = "text";
		$contentStr = "Welcome to wechat world!";
		$resultStr = sprintf($textTpl, $fromUsername, $toUsername, $time, $msgType, $contentStr);
		echo $resultStr;
	    } else {
		echo "Input something...";
	    }
        } else {
	    echo "";
	    exit;
        }
    }

    private function checkSignature()
    {
	global $config;

	if (!isset($config['wechat_token'])) {
	    throw new Exception('TOKEN not defined!');
	}
	$token = $config['wechat_token'];

        $signature = $_GET["signature"];
        $timestamp = $_GET["timestamp"];
        $nonce = $_GET["nonce"];

	$tmpArr = array($token, $timestamp, $nonce);
	sort($tmpArr, SORT_STRING); // use SORT_STRING rule
	$tmpStr = implode($tmpArr);
	$tmpStr = sha1($tmpStr);

	return ($tmpStr == $signature);
    }
}

/* vim:et:ts=4:sw=4: */
?>
