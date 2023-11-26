function refresh() {
    $.ajax({
        dataType: "json",
        success: function(data) {
            $('#refresh').html();
            if (data.success) {
                window.location.href = data.url;
            }
        }
    });
    setTimeout(refresh, 5000);
}

$(function(){
    refresh();
});
