// :/ vim: set fileencoding=utf-8 :
// RadioCUT main javascript file
/*global $,window,document,navigator,UserVoice,_gaq*/
/*jslint unparam: true, node: true */
var Utils = Utils || {};

(function(ns) {

    // este codigo fue sacado de http://stackoverflow.com/a/901144
    function getParameterByName(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? undefined : decodeURIComponent(results[1].replace(/\+/g, " "));
    }
    ns.getParameterByName = getParameterByName;

    function getHashParameterByName(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\#&]" + name + "=([^&#]*)"),
            results = regex.exec(location.hash);
        return results === null ? undefined : decodeURIComponent(results[1].replace(/\+/g, " "));
    }
    ns.getHashParameterByName = getHashParameterByName;

    function getCookieValue(a) {
        var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
        return b ? b.pop() : '';
    }
    ns.getCookieValue = getCookieValue;

})(Utils);
