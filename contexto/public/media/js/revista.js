$(document).ready(function() {
	$('#grid').click(function(event) {
		$('#container').toggleClass('grid');
		event.preventDefault();
	});

	$("a[rel^='prettyPhoto']").prettyPhoto();
});
