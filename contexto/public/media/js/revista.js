$(document).ready(function() {

	/**
	 * Tools
	 */
	$('#grid').click(function(event) {
		$('.container').toggleClass('showgrid');
		event.preventDefault();
	});

	var initialLeft = parseInt($('#tools').css("left"));
	$('#tools').hover(function() {
		$(this).animate({
			left: 0
		}, 'fast');
	}, function() {
		$(this).animate({
			left: initialLeft
		}, 'fast');
	});

	/**
	 * Galería
	 */
	$("a[rel^='galeria']").prettyPhoto();

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
