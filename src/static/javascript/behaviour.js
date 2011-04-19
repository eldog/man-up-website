/* specify the behaviour of all elements on the pages of the website here */
$(document).ready(function() {
    $('.tab-link').bind('click', function () {
        $('.tab-page').hide();
        $('#' + $(this).attr('id') + '-tab-page').show();
    });
});
