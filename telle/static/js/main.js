$(document).ready(function() {
    /* -------------------------------- *
    * Show/hide info panel
    * -------------------------------- */
    var INFO_PANEL_ID = null;
    $('.filter-item').on('click', function(e) {
        // if is button, dont show panel
        if($(e.target).is('path') || $(e.target).is('g') 
            || $(e.target).is('svg') || $(e.target).is('button'))
            return;
        // if is person, dont show panel
        if($(e.currentTarget).attr('type') == "person")
            return;
        var trakt_id = $(e.currentTarget).attr('trakt_id');
        // null
        if(INFO_PANEL_ID == null) {
            fillInfoPanel(trakt_id);
            setTimeout(triggerScroll, 100);
        }
        // if panel is open
        if (INFO_PANEL_ID != null ) {
            $('.info-pane').hide("blind",200);
            $('.info-pane .background img').removeClass('lazy_info');
            $('.info-pane-img img').removeClass('lazy_info');
            var info_id = $('.info-pane').attr('trakt_id');
            if(!$('.info-for-panel[trakt_id="'+info_id+'"]')[0].hasAttribute('loaded') 
                && $('.info-pane-img img').attr('src').indexOf("placeholder") == -1) {
                $('.info-for-panel[trakt_id="'+info_id+'"]').html($('.info-pane').html());
                $('.info-for-panel[trakt_id="'+info_id+'"]').attr('loaded',"true");
            }
        }
        // different IDs
        if(INFO_PANEL_ID != null && INFO_PANEL_ID != trakt_id){
            setTimeout(function() {fillInfoPanel(trakt_id)}, 200);
            setTimeout(triggerScroll, 200);
        }
        if(INFO_PANEL_ID == trakt_id) {
            INFO_PANEL_ID = null;
            $('.info-pane').attr("trakt_id",null);
        }
        else {
            INFO_PANEL_ID = trakt_id;
            $('.info-pane').attr("trakt_id",trakt_id);
        }
    });
    fillInfoPanel = function(trakt_id) {
        $('.info-pane').html($('.info-for-panel[trakt_id="'+trakt_id+'"]').html());
        if(!$('.info-for-panel[trakt_id="'+trakt_id+'"]')[0].hasAttribute('loaded')) {
            $('.info-pane .background img').addClass('lazy_info');
            $('.info-pane-img img').addClass('lazy_info');
        }
        $(function() {
          $("img.lazy_info").lazyload({
            effect: "fadeIn",
            failure_limit: Math.max($("img.lazy_info").length - 1, 0),
            effectspeed: 500,
            threshold:100
          });
        });
        $('.info-pane').show("blind",200);
    }

    /* -------------------------------- *
    * Resize text to fit in select divs
    * -------------------------------- */
    fontsize = function() {
    var $pos = $('.poster'),
      $fan = $('.fanart'),
      $pos_o = $('.poster .overlay-title'),
      $pos_p = $('.poster .placeholder'),
      $fan_o = $('.fanart .overlay-title'),
      $fan_p = $('.fanart .placeholder'),
      $fan_s = $('.fanart #left-sub');
    var pos_o_size = $pos.width() * $pos_o.attr('reg'),
      pos_p_size = $pos.width() * $pos_p.attr('reg'),
      fan_o_size = $fan.width() * $fan_o.attr('reg'),
      fan_p_size = $fan.width() * $fan_p.attr('reg'),
      fan_s_size = $fan.width() * $fan_s.attr('reg');
    if (pos_o_size < 20)
      pos_o_size = $pos.width() * $pos_o.attr('sm');
    if (pos_p_size < 20)
      pos_p_size = $pos.width() * $pos_p.attr('sm');
    if (fan_o_size < 20)
      fan_o_size = $fan.width() * $fan_o.attr('sm');
    if (fan_p_size < 20)
      fan_p_size = $fan.width() * $fan_p.attr('sm');
    if (fan_s_size < 20)
      fan_s_size = $fan.width() * $fan_s.attr('sm');

    $pos_o.css('font-size', pos_o_size);
    $pos_o.css('line-height', pos_o_size + "px");
    $pos_p.css('font-size', pos_p_size);
    $pos_p.css('line-height', pos_p_size + "px");
    $fan_o.css('font-size', fan_o_size);
    $fan_o.css('line-height', fan_o_size + "px");
    $fan_p.css('font-size', fan_p_size);
    $fan_p.css('line-height', fan_p_size + "px");
    $fan_s.css('font-size', fan_s_size);
    $fan_s.css('line-height', fan_s_size + "px");
  };
  var resizeTimer;
  $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(fontsize, 250);
  });
  fontsize();

});


// JQUERY -----------------------------------

jQuery(function($) {
  $(document).ready(function() {

    /* -------------------------------- *
     * Initialize main filters with isotope
     * -------------------------------- */
    var $win = $(window),
      $grid = $('.grid'),
      $default_filter = $('.filters .active').attr('data-filter');

    $grid.isotope({
      itemSelector: '.filter-item',
      layoutMode: 'fitRows',
      filter: $default_filter
    });

    $grid.on('layoutComplete', function() {
      $win.trigger("scroll");
    });

    // hash of functions that match data-filter values
    var filterFns = {};

    // filter based on clicked link
    $('.filters').on('click', '.filter', function() {
      var filterValue = $(this).attr('data-filter');
      // use filter function if value matches
      filterValue = filterFns[filterValue] || filterValue;
      $grid.isotope({
        filter: filterValue
      });
    });

    // change is-checked class on buttons
    $('.filters').each(function(i, filters) {
      var $filterGroup = $(filters);
      $filterGroup.on('click', '.filter', function() {
        $filterGroup.find('.active').removeClass('active');
        $(this).addClass('active');
      });
    });

    // reloads current filter
    reloadFilter = function() {
        $('.filter').each(function() {
            if($(this).hasClass('active'))
                $(this).click();
        });
    };

    // reloads the default filter
    reloadDefaultFilter = function() {
        var default_filter = $('#master-default-filter').val();
        $('.filter[data-filter=".' + default_filter + '"]').click();
    }

    /* -------------------------------- *
     * Convert svg files to inline svg
     * -------------------------------- */
    $('img.svg').each(function() {
      var $img = jQuery(this);
      var imgID = $img.attr('id');
      var imgClass = $img.attr('class');
      var imgURL = $img.attr('src');

      jQuery.get(imgURL, function(data) {
        var $svg = jQuery(data).find('svg');
        if (typeof imgID !== 'undefined')
          $svg = $svg.attr('id', imgID);
        if (typeof imgClass !== 'undefined')
          $svg = $svg.attr('class', imgClass + ' replaced-svg');
        $svg = $svg.removeAttr('xmlns:a');
        $img.replaceWith($svg);
      });
    });

    /* -------------------------------- *
     * Load imgages with lazyload
     * -------------------------------- */
    $(function() {
      $("img.lazy").lazyload({
        effect: "fadeIn",
        failure_limit: Math.max($("img.lazy").length - 1, 0),
        effectspeed: 500,
        threshold: 100
      });
    });
    window.addEventListener("load", function() {
      for (var i = 0; i < 500; i += 50)
        setTimeout(triggerScroll, i);
      setTimeout(triggerScroll, 10000);
    }, false);
    triggerScroll = function() {
      $win.trigger("scroll");
    }

    /* -------------------------------- *
     * Define smoothstate.js behavior
     * -------------------------------- */
    var show_loading = false,
        loading = "<div id='circle' style='opacity:1; filter:alpha(opacity=100)'>&#8226;&#8226;&#8226;</div>"
    $(function() {
      'use strict';
      var $page = $('#main'),
        options = {
          debug: true,
          prefetch: true,
          cacheLength: 0,
          forms: '#search-form',
          onBefore: function($currentTarget, $container) {
                if($currentTarget.is('#search-form') || $currentTarget.is('.full-info'))
                    show_loading = true;
          },
          onStart: {
            duration: 350,
            render: function($container) {
                $container.addClass('is-exiting');
                $('.topbar').addClass('no-hover');
                $('.sidebar').addClass('no-hover');
                $('.info-pane').hide("blind",200);
                smoothState.restartCSSAnimations();
                if(show_loading)
                    $container.append(loading);
            }
          },
          onReady: {
            duration: 0,
            render: function($container, $newContent) {
                if(show_loading)
                    show_loading = false;
                $container.removeClass('is-exiting');
                $container.html($newContent);
                for (var i = 0; i < 500; i += 50)
                    setTimeout(triggerScroll, i);
                setTimeout(triggerScroll, 10000);
            }
          }
        },
        smoothState = $page.smoothState(options).data('smoothState');
    });

    /* -------------------------------- *
     * Initiate vague.js behavior
     * -------------------------------- */
    var vague = $('.content').Vague({
        intensity:      30,
        forceSVGUrl:    false, 
        animationOptions: {
          duration: 0
        }
    });    

    /* -------------------------------- *
     * Options pull down menus
     * -------------------------------- */
    if (Modernizr.touch) {
        $(".radio-options").bind("click", function(event) {
            if (!($(this).parent('.radio-container').hasClass("active")))   {
            $(this).parent('.radio-container').addClass("active"); 
            event.stopPropagation();
            }
        }); 
        $(".toggle").bind("click", function(){ 
            $(this).parents('.radio-container').removeClass("active"); 
            return false;
        });  
    }

    /* -------------------------------- *
     * Popup Behavior
     * -------------------------------- */
    var popup = $('.popup'),
        popup_list = $('.list-popup'),
        popup_settings = $('.settings-popup'),
        popup_overlay = $('.blocker-overlay');

    jQuery.fn.setup = function (popup_name) {
        popup_name.css("position","absolute");
        popup_name.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) + 
                                                    $(window).scrollTop()) + "px");
        popup_name.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) + 
                                                    $(window).scrollLeft()) + "px");
        popup_name.draggable();
        $(document).on('mousedown',function (e) {
        if (!popup_name.is(e.target) 
            && popup_name.has(e.target).length === 0) {
            fadeOutPopup(popup_name);
        }
    });
    }
    fadeInPopup = function (popup_name) {
        $('.info-pane').hide("blind",200);
        popup_overlay.show();
        popup_name.setup(popup_name);
        popup_name.fadeIn(250);
        vague.blur();
    };
    popup_overlay.hide();
    popup.hide();
    fadeOutPopup = function(popup_name) {
        popup_overlay.hide();
        popup_name.fadeOut(250);
        vague.unblur();
        $(document).off('mousedown');
    }

    $('.options-icon').on('click',function() {
        var $master_filters = $('#master-filters').attr('class').split(" "),
            trakt_id = $(this).parent().attr('trakt_id');
        var $filters = $('.filter-item[trakt_id="'+trakt_id+'"]').attr('class').split(" ");

        // clear previous selections from popup
        for(var j=0; j< $master_filters.length; j++)
            $('.list-popup #list-' + $master_filters[j] + '-check').prop('checked', false);

        // set popup trakt_id
        popup_list.attr('trakt_id',trakt_id);

        // mark all lists the item is in
        for (var i = 0; i < $filters.length; i++)
            for(var j=0; j< $master_filters.length; j++)
                if($filters[i] == $master_filters[j])
                    $('.list-popup #list-' + $filters[i] + '-check').prop('checked', true);
        fadeInPopup(popup_list);
    });
    fadeOutListPopup = function() {
        fadeOutPopup(popup_list);
    }
    $('.settings svg').on('click',function() {
        fadeInPopup(popup_settings);
    });
    fadeOutSettingsPopup = function() {
        fadeOutPopup(popup_settings);
    }

    var show_space = $('.search-title.shows').hasClass('space'),
        people_space = $('.search-title.people').hasClass('space');
    
    $('.filters').on('click', '.filter', function() {
        console.log($(this));
        var data_filter = $(this).attr("data-filter");
        console.log(data_filter);
      if(data_filter == ".movies") {
        $('.search-title.movies').fadeIn();
        $('.search-title.shows').fadeOut();
        $('.search-title.people').fadeOut();
      }
      else if(data_filter == ".shows") {
        $('.search-title.movies').fadeOut();
        $('.search-title.shows').removeClass('space');
        $('.search-title.shows').fadeIn();
        $('.search-title.people').fadeOut();
      }
      else if(data_filter == ".people") {
        $('.search-title.movies').fadeOut();
        $('.search-title.shows').fadeOut();
        $('.search-title.people').removeClass('space');
        $('.search-title.people').fadeIn();
      }
      else {
        $('.search-title.movies').fadeIn();
        if(show_space)
            $('.search-title.shows').addClass('space');
        $('.search-title.shows').fadeIn();
        if(people_space)
            $('.search-title.people').addClass('space');
        $('.search-title.people').fadeIn();
      }
    });

  });
});
