$(document).ready(function() {
	$('#grid').click(function(event) {
		$('#container').toggleClass('grid');
		event.preventDefault();
	});
});
