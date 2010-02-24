jQuery(document).ready(function($){
  $.each(achievements, function(index, ach) {
    $('<div class="achievement">'+ach.display+'</div>').appendTo('body');
    setTimeout(function() {
      $('.achievement').fadeOut();
    }, 5000);
  });
});