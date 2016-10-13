function showMsg(msg){
    $(".comment-msg-info").removeClass("hide").text(msg).slideDown();
}

$(".delete-comment").click(function(evt){
    evt.preventDefault();
    var $this = $(evt.currentTarget);
    var id = $this.data("id"),
        comment = $this.parents("tr").find(".col-comment").text();
    
    $.postJson("/admin/comment/delete", {comment_id:id, _xsrf:window.dataObj._xsrf},
               function(res){
                   if (res.success){
                       showMsg("comment: " + id + " delete success.");
                       $this.parents("tr").remove();
                   }else{
                       showMsg("comment: " + id + "delete failed.");
                   }
               });
});

$(".saved-tags").delegate(".tag-button", "click",  function(evt){
    var $t = $(evt.currentTarget),
        tag = $t.data("text");

    if ($t.hasClass("active")){
        remove_tag(tag);
        $t.removeClass("active");
    }else{
        add_tag(tag);
        $t.addClass("active");
    }
    evt.preventDefault();
});

$("#input-tags").keypress(function(evt){
    var tags = $(this).val().split(" ");
    var $saved_tags = $(".saved-tags .tag-button");
    for (var j = 0; j < $saved_tags.length; j++){
        var active = false;
        for (var i = 0; i < tags.length; i++){
            if (tags[i] == "")
                continue;
            if (tags[i] == $($saved_tags[j]).data("text")){
                $($saved_tags[j]).addClass("active");
                active = true;
                break;
            }
        }

        if (!active)
            $($saved_tags[j]).removeClass("active");
    }
});

function remove_tag(tag){
    var tags = $("#input-tags").val().split(" ");
    var newTags = new Array()
    for (var i = 0; i < tags.length; i++){
        if (tags[i] != "" && tags[i] != tag)
            newTags.push(tags[i]);
    }
    $("#input-tags").val(newTags.join(" "));
}


function add_tag(tag){
    var tags = $("#input-tags").val().split(" ");
    var newTags = new Array()
    for (var i = 0; i < tags.length; i++){
        if (tags[i] != "" && tags[i] != tag)
            newTags.push(tags[i]);
    }
    newTags.push(tag);
    $("#input-tags").val(newTags.join(" "));    
}
