// $('table').on('click', '.delete', function(e) {

//     if($('table tr').length>1) {
//         $(this).closest('tr').remove();
//         $('td.num').text(function (i) {
//           return i + 1;
//         });
          
//     }

//     return false;
// });


  $('table').each(function(){
    $('th:first-child, thead td:first-child', this).each(function(){
      $(this).before('<th>ID</th>');
    });
    $('td:first-child', this).each(function(i){
      $(this).before('<td>'+(i+1)+'</td>');
    });
  });