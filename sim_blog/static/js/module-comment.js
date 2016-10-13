if (!console){
    console = Object();
    console.log = function(){};
}

function refreshCap(capid, capsrc){
    $.postJson("/cap",{_xsrf: window.dataObj._xsrf},function(res){
        if (res.success){
            $("#module-comment img.cap_src").attr("src", res.capsrc);
            $("#module-comment #cap_id").val( res.capid);
        }
    });
}

function showMsg(msg){
    $("#module-comment .comment-msg").text(msg).removeClass("hide").slideDown();
}

$("#module-comment #btn-submit").on("click", function(evt){
    evt.preventDefault();

    var params = {
        _xsrf: window.dataObj._xsrf,
        author_name:$("#module-comment #author_name").val().trim(),
        author_email:$("#module-comment #author_email").val().trim(),
        author_url:$("#module-comment #author_url").val().trim(),
        text:$("#module-comment #text").val(),
        cap_id:$("#module-comment #cap_id").val(),
        cap_code:$("#module-comment #cap_code").val().trim()};
    console.log(params);
    
    if (params.author_name == "")        
        return showMsg("Please let me know your name.");
    if (params.author_email == "")
        return showMsg("Please let me know your email, It's promised that it's only used for contacting you.");
    if (params.text == "")
        return showMsg("You must be kidding me!");
    if (params.cap_id == "")
        return showMsg("Getting captcha code failed, try click the captcha img to refresh. If you still counter this problem, please let me know, monklof at gmail.com.");

    if (params.cap_code == "")
        return showMsg("Please input the captcha code to ensure that you are human, not robot.");

    $.postJson($("#module-comment #form-comment")[0].action,
               params, function(res){
                   if (res.success)
                       window.location.reload();
                   else{
                       if (res.error_text)
                           showMsg(res.error_text);
                       else
                           showMsg("Captcha code error");
                       refreshCap();
                   }
               });
});


$("#module-comment #author_name,#module-comment  #author_url,#module-comment  #author_email,#module-comment   #text").on("click", function(evt){
    if ($("#module-comment #cap_id").val() != "")
        return;
    refreshCap();
});

$("#module-comment .cap_src").on("click", function(evt){
    refreshCap();
});

$("#module-comment .at-comment").on("click", function(evt){
    /* 回复评论 */
    var author_name = $(this).data("author");
    var textObj = $("#module-comment #text")[0];
    insertText(textObj, "@["+author_name+"] ");
});

function insertText(obj,str) {
    if (document.selection) {
        var sel = document.selection.createRange();
        sel.text = str;
    } else if (typeof obj.selectionStart === 'number' && typeof obj.selectionEnd === 'number') {
        var startPos = obj.selectionStart,
        endPos = obj.selectionEnd,
        cursorPos = startPos,
        tmpStr = obj.value;
        obj.value = tmpStr.substring(0, startPos) + str + tmpStr.substring(endPos, tmpStr.length);
        cursorPos += str.length;
        obj.selectionStart = obj.selectionEnd = cursorPos;
    } else {
        obj.value += str;
    }
}
