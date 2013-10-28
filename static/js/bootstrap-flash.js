/*
    Bootstrap Flash
    Version: 1.0
    A small lib to display notifications by @vsergeyev
    https://github.com/vsergeyev/bootstrap-flash

    Twitter Bootstrap (http://twitter.github.com/bootstrap).
*/

(function(){
    $(document).ready(function () {
        $("body").prepend('<div class="bootstrap-flash alert alert-success alert-error hide" style="position:absolute;top:50px;left:25%;width:50%;float:left;z-index:1500;"><a class="close" href="#" onclick="$(this).parent().hide();return false;">&times;</a><p style="margin:0!important"></p></div>');
    });

    // Hide alert in 10 seconds
    setInterval(function() {
        $(".bootstrap-flash").fadeOut("slow");
    }, 5000);

    this.flash = function(msg, err) {
        var box = $(".bootstrap-flash");
        console.log(box);
        if (err == "error") {
            box.removeClass("alert");
            box.removeClass("alert-success");
            box.addClass("alert-error");
        }
        else if(err == "success") {
            box.removeClass("alert-error");
            box.addClass("alert-success");
            //box.removeClass("alert");
        }
        else {
            box.removeClass("alert-error");
            box.removeClass("alert-success");
            //box.addClass("alert");
        }

        box.find("p").html(msg);
        box.show();
    }
}).call(this);