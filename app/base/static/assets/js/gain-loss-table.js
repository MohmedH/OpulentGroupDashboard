const $tableID = $('#tableT');
const $BTN = $('#export-btn');
const $EXPORT = $('#export');
const dataSend = {}
jQuery.fn.pop = [].pop;
jQuery.fn.shift = [].shift;
var today = new Date();
var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();

$('.table-add-new').on('click', 'i', () => {

    var newTr = `
        <tr class="hide">
        <td class="pt-3-half" style="color: white;" contenteditable="true">`+date+`</td>
        <td class="pt-3-half" style="color: white;" contenteditable="true">$0</td>
        <td class="pt-3-half" style="color: white;" contenteditable="true">gain</td>
        <td>
        <span>
            <button class="button-save" id="button-remove"></button>
        </span>
        </td>
        </tr>`;

    $('tbody').append(newTr);

});

$tableID.on('click', '.button-save', function () {
    
    $(this).addClass( "onclic");
    var button = $(this);
    
    //invalidate($(this));
    //validate($(this))

    function invalidate($obj) {
    setTimeout(function() {
        ( $obj ).removeClass( "onclic" );
        ( $obj ).addClass( "invalidate", 1000);
        callback($obj);
    }, 1000);  
    }

    function validate($obj) {
    setTimeout(function() {
        ( $obj ).removeClass( "onclic" );
        ( $obj ).addClass( "validate", 1000);
        callback($obj);
    }, 1000);  
    }

    function callback($obj) {
    setTimeout(function() {
        ( $obj ).removeClass( "validate" );
        ( $obj ).removeClass( "invalidate" );
    }, 1500 );
    }

    const $rows = $tableID.find('tr:not(:hidden)');
    const headers = [];
    var $row = $(this).closest("tr"),       // Finds the closest row <tr> 
    $tds = $row.find("td");             // Finds all children <td> elements
    const data = {};

    //First part is to get the headers, shouldnt change but incase they ever do
    $($rows.shift()).find('th:not(:empty)').each(function () {
        if($(this).text().toLowerCase() != "remove" && $(this).text().toLowerCase() != "save" ){
            //console.log(headers)
            headers.push($(this).text().toLowerCase());
        }
    });
    //Now we have the table headers!
    $.each($tds, function(i) {         // Visits every single <td> element
        if ($(this).hasClass("pt-3-half")){  // Check to make sure its the text fields
            //console.log($(this).text());   // Prints out the text within the <td>
            data[headers[i]] = $(this).text()
        }
    });

    //console.log(data)
    $.ajax({
        url: '/update/gains_losses',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(){
            console.log( 'Worked' );
            validate(button);
            md.showNotification('top','center','success','Saved For Date: '+ data['date'] + ' Successfully, you can refresh to view changes!')
        },
        error: function( jqXhr, textStatus, errorThrown ){
            console.log( errorThrown );
            invalidate(button);
            md.showNotification('top','center','danger','Error! Could Not Save')
        }
    });
    
});