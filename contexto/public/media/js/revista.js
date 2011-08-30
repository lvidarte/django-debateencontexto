$(document).ready(function() {

	/**
	 * Guías
	 */
	$('#grid').click(function(event) {
		$('#container').toggleClass('grid');
		event.preventDefault();
	});

	/**
	 * Galería
	 */
	$("a[rel^='prettyPhoto']").prettyPhoto();

	/**
	 * Menú
	 */
	$('#menu li > a').click(function(event) {
		event.preventDefault();
		$('.submenu').hide();
		$('#' + this.getAttribute('rel')).show();
	});

	$('.submenu').hide();
	$('#' + submenu).show();

});
