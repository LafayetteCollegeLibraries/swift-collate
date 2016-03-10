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
	    $.get('/collate/search/transcripts/' + poemId, function(response) {
		    
		    var data = JSON.parse(response);

		    $.each(data.items, function(i, e) {
			    $("#base-text-select2").append('<option value="' + e + '">' + e + '</option>');
			});
		});

	    $("#base-text-select2").select2({
		    placeholder: "Select a Transcript",
			allowClear: true,
			}).on("select2:select", function(event) {
				var slug = $(event.target).val();

				// Find the checkbox field for this text as a variant, deselect it, and disable it
			    });

	});
}(jQuery));
