table_row_default = '<tr class="sortable"><td class="db_name">not_set</td><td class="name-td">ROLE_NAME_PLACEHOLDER</td><td class="rank">-1</td><td class="right-button"><button class="btn btn-danger btn-delete"><i class="icon-remove"></i></button></td></tr>'
$(document).ready(function() {
    sortable_roles()

    $('#role-form').submit(function(event){
        event.preventDefault();

        var new_role = $('#role-form #new-role-input')[0].value;

        $('#role-table tr:last').after(table_row_default.replace('ROLE_NAME_PLACEHOLDER', new_role))
        sortable_roles()
        submit_roles('#role-form')
    });

    //Delete button in table rows
    $('table').on('click','.btn-delete',function() {
        tableID = '#' + $(this).closest('table').attr('id');
        var row = $(this).closest('tr')
        r = confirm('Delete role '+ $('.name-td', row)[0].innerText);
        if(r) {
            row.remove();
            submit_roles(tableID);
        }
    });

    // Listen to changes in the AuthModels and submit them
    $('.selectpicker').on('changed.bs.select', function(e){
        submit_auth(this.id);
    })
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
    var table_name = "#role-table"
    $(table_name + " tbody").sortable({
        helper: fixHelperModified,
        stop: function(event,ui) {submit_roles(table_name)},
        items: $('#role-table .sortable'),
    }).disableSelection();
};

//Rerank table rows
function rerank_table(tableID) {
    count = $(tableID + ' tr').length + 1;
    $(tableID + " tr").each(function() {
        count = count - 1;
        $(this).find('.rank').html(count);
    });
}

//Send table data to backend after change
function submit_roles(tableID) {
    rerank_table(tableID);
    table_data = []
    $(tableID + " tr").each(function() {
        var data = {
            'rank': $(this).find('.rank').html(),
            'display_name': $(this).find('.name-td').html(),
            'name': $(this).find('.db_name').html(),
        }
        table_data.push(data)
    });

    $.ajax({
        'url': 'permissions/update_roles',
        'data': {'data': JSON.stringify(table_data)},
        'dataType': 'json',
        'error': function(error){console.log(error)},
        'method': 'POST',
    })
    console.log(table_data)
}

function submit_auth(authID) {
    var data = {}
    data[authID] = $('#'+authID).val()
    $.ajax({
        'url': 'permissions/auth_update',
        'data': data,
        'dataType': 'json',
        'error': function(error){console.log(error)},
        'method': 'POST',
    });
}