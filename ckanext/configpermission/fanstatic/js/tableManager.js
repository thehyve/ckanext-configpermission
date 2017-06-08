table_row_default = '<tr class="sortable"> <td class="name-td">ROLE_NAME_PLACEHOLDER</td><td style="display:none">-1</td><td class="right-button"><button class="btn btn-danger btn-delete"><i class="icon-remove"></i></button></td></tr>'
$(document).ready(function() {
    sortable_roles()

    $('#role-form').submit(function(event){
        event.preventDefault();

        var new_role = $('#role-form #new-role-input')[0].value;

        $('#role-table tr:last').after(table_row_default.replace('ROLE_NAME_PLACEHOLDER', new_role))
        sortable_roles()
    });

    //Delete button in table rows
    $('table').on('click','.btn-delete',function() {
        tableID = '#' + $(this).closest('table').attr('id');
        var row = $(this).closest('tr')
        r = confirm('Delete role '+ $('.name-td', row)[0].innerText);
        if(r) {
            row.remove();
            renumber_table(tableID);
        }
    });
});

//Helper function to keep table row from collapsing when being sorted
var fixHelperModified = function(e, tr) {
    var $originals = tr.children();
    var $helper = tr.clone();
    $helper.children().each(function(index)
    {
      $(this).width($originals.eq(index).width())
    });
    return $helper;
};

//Make role table sortable
function sortable_roles(){

    $("#role-table tbody").sortable({
        helper: fixHelperModified,
        stop: function(event,ui) {renumber_table('#role-table')},
        items: $('#role-table .sortable'),
    }).disableSelection();
};

//Renumber table rows
function renumber_table(tableID) {
    $(tableID + " tr").each(function() {
        count = $(this).parent().children().index($(this)) + 1;
        $(this).find('.priority').html(count);
    });
}