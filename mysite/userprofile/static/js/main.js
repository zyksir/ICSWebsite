$(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

   /* $('#recent-posts').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!");  // sanity check
        var post_id = $('#div_post').attr('postid');
        add_comment(post_id);
        console.log($(this).parent());
    });*/
    

    //The below function only works in case of embeded in original html file...I don't know why... 
    /*function add_comment(post_id) {
    $('.ajaxProgress').show();
    console.log("add comment is working!"); // sanity check
    var commentBoxId = '#comment-text'+ post_id;
    var listId = '#comment-list'+ post_id;
    console.log((this).parents(':eq(3)'))
    $.ajax({
        url:"../../profile/comment/"+ post_id +"/",
        type:"POST",
        assync: true,
        data: { comment : $(commentBoxId).val(), csrfmiddlewaretoken: '{{ csrf_token }}' },

        success : function(json) {
            $(commentBoxId).val(''); // remove the value from the input
            console.log(json);
            $(listId).html('').load('http://127.0.0.1:8000/profile/list_comments/'+post_id+'/');
        },
        
        error : function(jqXHR, textStatus, errorThrown) {
        console.log('error');
        console.log(jqXHR, textStatus, errorThrown);
        },

    })

    };*/

});
