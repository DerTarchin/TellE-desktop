jQuery(function($) {
  $(document).ready(function() {
    var $win = $(window);

    /* -------------------------------- *
     * Show/hide extra cast/crew
     * -------------------------------- */
    $('.cast_hidden').hide();
    $('.crew_hidden').hide();

    $('#showCast').on('click',function(){
      $('#showCast').fadeOut(100);
      setTimeout(function(){
        $(".cast_hidden").fadeIn(350);
        setTimeout(function(){$win.trigger("scroll");},350);
        setTimeout(function(){$win.trigger("scroll");},450);
      },100);
      
    });

    $('#showCrew').on('click',function(){
      $('#showCrew').fadeOut(100);
      setTimeout(function(){
        $(".crew_hidden").fadeIn(350);
        setTimeout(function(){$win.trigger("scroll");},350);
        setTimeout(function(){$win.trigger("scroll");},450);
      },100);
      
    });

    /* -------------------------------- *
    * Resize text to fit in select divs
    * -------------------------------- */
    fontsize_info = function() {
      var $but = $('.filter-button .more-button');
      var but_size = $but.width() * $but.attr('reg');

      $but.css('font-size', but_size);
      $but.css('line-height', but_size + "px");
    };
    var resizeTimer;
    $(window).resize(function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(fontsize_info, 250);
    });
    fontsize_info();
    setTimeout(fontsize_info, 2000);

    /* -------------------------------- *
    * Cast/Crew redirect
    * -------------------------------- */
    $('.poster:not(.season-item)').on('click',function() {
      if(!$(this).hasClass('filter-button')) {
        $('#info-link').attr('href',$(this).attr('url'));
        $('#info-link')[0].click();
      }
    });

    /* -------------------------------- *
     * Grid Item
     * -------------------------------- */
    var lastSeasonItem = "";
    $('.season-item').on('click',function() {
      var season = $(this).closest('.season-item').attr('season');
      var info_div = '<div class="link-row grid-info" season="'
        + season + '"></div>';

      // dont pre-hide it if current id
      if(lastSeasonItem != season)
        $('.grid-info').hide("blind", 200);

      // check if previously generated, show/hide it
      if($('.grid-info[season="'+season+'"]').length)
        $('.grid-info[season="'+season+'"]').toggle("blind", 200);

      // otherwise generate and show new
      else {
        $(info_div).insertAfter($(this).closest('.season-row')).show("blind", 200);
        $('.grid-info[season="'+season+'"]').append($('.grid-info-contents[season="' + season +'"]').html());
        $(function() {
          $("img.lazy_episode").lazyload({
            effect: "fadeIn",
            failure_limit: Math.max($("img.lazy_info").length - 1, 0),
            effectspeed: 500,
            threshold:100
          });
        });
        setTimeout(function(){$win.trigger("scroll");},200);
      }
      lastSeasonItem = season;
    });
    
  });
});

// MANAGE EPISODES /////////////////////////////////////////
manage_episode = function(trakt_id, season, episode) {

  var manage_url = $('#manage_episode_url').val();

  send_data = {
      trakt_id: trakt_id,
      csrfmiddlewaretoken: csrf
  };

  $.ajax({
    url: manage_url,   
    data: send_data,
    type: "POST",
    dataType : "json",
    success: function(json) {
      if (!json.error) {
        // from unwatch to watched
        if($('.episode-watch[w="f"][se='+season+'][ep='+episode+']').is(":visible")) {
          $('.episode-watch').each(function() {
            if($(this).attr("w")=="f") {
              if(parseInt($(this).attr("se")) < parseInt(season))
                $(this).hide();
              else if(parseInt($(this).attr("se")) > parseInt(season))
                $(this).show();
              else if(parseInt($(this).attr("se")) == parseInt(season)) {
                if(parseInt($(this).attr("ep")) <= parseInt(episode))
                  $(this).hide();
                else
                  $(this).show(); }
              }
            else if($(this).attr("w")=="t") {
              if(parseInt($(this).attr("se")) < parseInt(season))
                $(this).show();
              else if(parseInt($(this).attr("se")) > parseInt(season))
                $(this).hide();
              else if(parseInt($(this).attr("se")) == parseInt(season)) {
                if(parseInt($(this).attr("ep")) <= parseInt(episode))
                  $(this).show();
                else
                  $(this).hide();
              }
            }
          });
        }
        // from watched to unwatched
        else {
          $('.episode-watch').each(function() {
            if($(this).attr("w")=="f") {
              if(parseInt($(this).attr("se")) < parseInt(season))
                $(this).hide();
              else if(parseInt($(this).attr("se")) > parseInt(season))
                $(this).show();
              else if(parseInt($(this).attr("se")) == parseInt(season)) {
                if(parseInt($(this).attr("ep")) >= parseInt(episode))
                  $(this).show();
                else
                  $(this).hide(); }
              }
            else if($(this).attr("w")=="t") {
              if(parseInt($(this).attr("se")) < parseInt(season))
                $(this).show();
              else if(parseInt($(this).attr("se")) > parseInt(season))
                $(this).hide();
              else if(parseInt($(this).attr("se")) == parseInt(season)) {
                if(parseInt($(this).attr("ep")) >= parseInt(episode))
                  $(this).hide();
                else
                  $(this).show();
              }
            }
          });
        }
      }
      else 
        console.log("JSON ERROR STATUS: " + json.error);
    },
    error: function(xhr, status, errorThrown) {
        alert("Error: " + errorThrown);
    },
    complete: function( xhr, status ) {
      return;
    }
  });
};