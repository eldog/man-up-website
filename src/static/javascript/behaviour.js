/* specify the behaviour of all elements on the pages of the website here */
$(document).ready(function() {
    $('.tab-link').bind('click', function () {
        $('.tab-page').hide();
        $('#' + $(this).attr('id') + '-tab-page').show();
    });
    $('#start_date').datepicker({dateFormat: 'yy-mm-dd'});
    $('#end_date').datepicker({dateFormat: 'yy-mm-dd'});
});
