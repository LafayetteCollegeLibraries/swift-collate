/**
 *
 */

'use strict';

(function($) {

    $(document).ready(function(e) {

	    /**
	     * Format the data returned from the server
	     *
	     */
	    function formatData (data) {
		var markup = "" + data + "";

		return markup;
	    };

	    /**
	     * Format the data selected within the widget
	     *
	     */
	    function formatDataSelection (data) {
		return data;
	    };

	    /**
	     *
	     */

	    var pathname = window.location.pathname;

	    var poemId = $('#poem').val();
	    /*
	    $.get('/collate/search/transcripts/' + poemId, function(response) {
		    
		    var data = JSON.parse(response);

		    $.each(data.items, function(i, e) {
			    $("#base-text-select2").append('<option value="' + e + '">' + e + '</option>');
			});
		    $("#base-text-select2").val(data.items[0]);
		});
	    */

	    $("#base-text-select2").select2({
		    placeholder: "Select a Transcript",
			allowClear: true,
			}).on("select2:select", function(event) {
				var slug = $(event.target).val();

				// Find the checkbox field for this text as a variant, deselect it, and disable it
				var $checkbox = $('input[type="checkbox"][value="' + slug + '"]');
				$checkbox.prop('disabled', true);
				$checkbox.prop('checked', false);

				// Avoid having to traverse the DOM
				var $previous = $(document).data('base-text-select2');
				if($previous) {
				    $previous.prop('disabled', false);
				}

				$(document).data('base-text-select2', $checkbox);
			    });

	    /**
	     * Handling for the selection of the base texts for collation
	     *
	     */
	    $('.input-base-text').change(function(event) {
		    // This also shouldn't be enabled through any other means
		    /*
		    if( $(this).prop('disabled') ) {
			event.preventDefault();
		    }
		    */

		    // Disable the selection for the other base texts
		    $('.input-base-text').not($(this)).prop('disabled',  $(this).prop('checked'));

		    // Disable the selection for this text as a variant text
		    $('.input-variant[value="' + $(this).val() + '"]').prop('disabled',  $(this).prop('checked'));
		});

	    /**
	     * Handling for the selection of variant texts for collation
	     *
	     */
	    $('.input-variant').change(function(event) {
		    // This also shouldn't be enabled through any other means
		    /*
		    if( $(this).prop('disabled') ) {
			event.preventDefault();
		    }
		    */

		    // Disable the selection for this text as a base text
		    $('.input-base-text[value="' + $(this).val() + '"]').prop('disabled',  $(this).prop('checked'));
		});
	    
	    /**
	     * Initialize the form with fully-enabled checkboxes
	     *
	     */
	    $('.input-base-text, .input-variant').prop('disabled',  false);

	    /**
	     * For the rendering of part of speech tags
	     *
	     */
	    

	});
}(jQuery));
