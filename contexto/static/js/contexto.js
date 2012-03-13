$(function() {

    /**
     * Fix sub nav on scroll
     */
    var $win = $(window)
      , $nav = $('.menu')
      , navTop = $('.menu').length && $('.menu').offset().top
      , isFixed = 0;

    processScroll();

    $win.on('scroll', processScroll);

    function processScroll() {
      var i, scrollTop = $win.scrollTop();
      if (scrollTop >= navTop && !isFixed) {
        isFixed = 1;
        $nav.addClass('menu-fixed');
      } else if (scrollTop <= navTop && isFixed) {
        isFixed = 0;
        $nav.removeClass('menu-fixed');
      }
    }

    /**
     * Gallery
     */
    $("a[rel^='gallery']").prettyPhoto();

    /**
     * Carousel
     */
    $('#myCarousel').carousel();

});
