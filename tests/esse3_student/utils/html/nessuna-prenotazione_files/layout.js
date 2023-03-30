$(function() {

	/*
	 * apri/chiudi
	*/
	
	$('[data-toggle]').on('click', function(){

		var toggle = $(this).data('toggle');

		if (toggle === 'modal'){
			return true;
		}
		
		var target = $('#' + toggle);

		target.toggleClass('is-open');

	
		target.attr('aria-hidden') == "true" ? target.attr('aria-hidden', "false") : target.attr('aria-hidden', "true")
		

		if($(this).data('toggle') === 'secondary-menu-list'){

			var menu = $('#secondary-menu');

			menu.hasClass('is-open') ? menu.removeClass('is-open') : menu.addClass('is-open')
		}

		if($(this).hasClass('masthead_hamburger')){
            document.body.style.overflow = 'hidden';
		}

		if($(this).hasClass('masthead_menu_close')){
            document.body.style.overflow = 'visible';
		}

		if($(this).attr('aria-expanded') == "false") {

			$('[data-toggle="'+$(this).data('toggle')+'"]').each(function(){
				$(this).attr('aria-expanded',true);
			})
		}

		else if($(this).attr('aria-expanded') == "true"){
			$('[data-toggle="'+$(this).data('toggle')+'"]').each(function(){
				$(this).attr('aria-expanded',false);
			})
		}

		if($(this).data('scroll')){
			var scroll = $($(this).data('scroll')).offset().top;
			$(window).scrollTop(scroll);
		}


		if($(this).data('focus')){
			if($(this).attr('aria-expanded')==='true' || $(this).attr('id')=='chiudi-menu-principale') {
				$($(this).data('focus')).trigger('focus');				
			}
		}

		if($(this).data('toggle') === 'main-navigation'){

			if(target.attr('aria-hidden') == "false") {

				$('.masthead_top').attr('aria-hidden','true');
				$('body > *').each(function(){

					if(!$(this).hasClass('masthead')) {
						$(this).attr('aria-hidden','true');
					}
				})
			}
			else {
				$('body > *').each(function(){
					if(!$(this).hasClass('masthead')) {
						$(this).removeAttr('aria-hidden');
					}
				})
				$('.masthead_top').attr('aria-hidden','false');
			}
		}

		if($(this).data('toggle') === 'help-panel'){


			var menu = $('#help'),
				classes = ['l-content-container','l-container','l-sidebar','l-sidebar-right','l-header','help'];




			if(menu.hasClass('is-open') ) {
				menu.removeClass('is-open');
				$('#help-panel').attr('aria-hidden','true');
				$('.help-icon').trigger('focus');

				$('body > *').each(function(){
					if(!$(this).hasClass('help-panel')) {
						$(this).removeAttr('aria-hidden');
						$('.l-sidebar-left').removeAttr('aria-hidden');
					}

				})
			}
			else {
				menu.addClass('is-open');

				$('#help-panel').attr('aria-hidden','false');
				$('#help-title').trigger('focus');

				$('body > *').each(function(){
					if(classes.indexOf($(this).attr('class'))==-1) {
						$(this).attr('aria-hidden','true');
						$('.l-sidebar-left').attr('aria-hidden','true');
					}
				})
			}

		}

		return false;
	});


	/*
	 * menu in pagina
	*/



	function conMenu () {

	    	$('.salta-menu-mobile').hide();
	    	$('.salta-menu-desktop').show();

	    	if($('body').hasClass('has-menuInPagina')) {
		    	$('.masthead_hamburger').hide();
		    	$('#main-navigation').removeAttr('aria-hidden').removeAttr('aria-modal').removeAttr('role');
		    	$('.l-sidebar-left-placeholder').remove();
		    	$( '#main-navigation' ).prependTo('.l-sidebar-left');
		    	$( 'body' ).addClass('js-menuInPagina');
	    	}
	}

	function senzaMenu () {
	    	
	    	$('.salta-menu-mobile').show();
	    	$('.salta-menu-desktop').hide();	

	    	if($('body').hasClass('has-menuInPagina')) {
	    		$( '#main-navigation' ).insertAfter('.masthead_top').removeClass('is-static').attr('aria-modal','true').attr('role','dialog');
	    		$( 'body' ).removeClass('js-menuInPagina');
	    		$('.masthead_hamburger').show();
	    		$('#main-navigation').attr('aria-hidden','true');
	    	}

	}

	enquire.register("screen and (min-width:1366px)", {

	    match : function() {
	    	conMenu();
	    },     

	    unmatch : function() {
	    	senzaMenu();
	    },

	    setup : function() {
	    	if($(window).width()<1366){
	    		senzaMenu();
	    	}
	    }

	});
	

	/*
	 * Gestione onclick sulle voci di menù
	*/
	$('.masthead_menu_body > ul > li.has-children:not(.masthead_usermenu_menu):not(.masthead_menu_body_comunita) > a').on('click', function() {

		$(this).next().toggleClass('is-open');
		$(this).parent().toggleClass('is-open');

		$(this).attr('aria-expanded') == 'false' ? $(this).attr('aria-expanded','true') : $(this).attr('aria-expanded','false');

		$('.masthead_menu_body > ul > li').not($(this).parent()).each(function(){
			if(!$(this).hasClass('is-hidden') && !$(this).hasClass('masthead_menu_body_comunita') && !$(this).hasClass('masthead_usermenu_menu')){
				$(this).addClass('is-hidden');
			}
			else if($(this).hasClass('is-hidden')){
				$(this).removeClass('is-hidden');
			}
		});

		return false;
	})

	// per rimuovere gli attributi aria- dal menu utente, perchè sempre aperto, e dal menu comunità perchè l'apertura/chiusura è governata diversamente
	$('.masthead_usermenu_menu > ul > li > a').removeAttr('aria-expanded').removeAttr('aria-controls');
	$('.masthead_menu_body > ul > li.masthead_menu_body_comunita > a').removeAttr('aria-expanded').removeAttr('aria-controls');
	
	/*
		secondary menu
	 */
	
	var width = 40;
	
	$('.secondary-menu li:not(.anchormenu) a').each(function(){
		width += $(this).width() + 30;
	});


	enquire.register("screen and (min-width:"+width+"px)", {

	    match : function() {
	    	$('.secondary-menu').addClass('is-visible');
	    	$('.secondary-menu').removeClass('is-hidden');
	    	$('.secondary-menu-list').attr('aria-hidden','false');
	    }

	});


	enquire.register("screen and (max-width:"+width+"px)", {

	    match : function() {
	    	$('.secondary-menu').removeClass('is-visible');
	    	$('.secondary-menu').addClass('is-hidden');
	    	$('.secondary-menu-list').attr('aria-hidden','true');

	    },     

	});

	/*
	 * scroll dei panel aperti (menu/help)
	 */

	$('[data-toggle="main-navigation"],[data-toggle="help"]').on('click', function(e){
	 	if(!$('body').hasClass('is-locked')){
	 		$('body').addClass('is-locked');
	 	}
	 	else {
	 		$('body').removeClass('is-locked');
	 	}
	})



/** fine implementazione esterna **/


	// https://codepen.io/sebastian-julius/pen/bCsJv
	// Find all internal anchor links and
	// circumvent the base tag behavior
	
	$('a[href^="#"]').on('click', function(event) { 
	
	  event.preventDefault();
	
	  // directly jump to the anchor
	  document.location.hash =   
	      $(this).attr('href').replace('#','');
	  
	});

});