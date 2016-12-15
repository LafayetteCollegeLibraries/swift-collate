/**
 * jQuery widget integration and behavior
 *
 */

'use strict';

(function($) {

    $(document).ready(function(e) {

	    /**
	     * Widgets for the collation viewing interface
	     *
	     */
	    $('#reset-scroll').click(function(event) {
		    event.preventDefault();
		    $('html, body').animate({ scrollTop: 0 }, 500);
		    return false;
		});

	    $('#toggle-line-variation').click(function(e) {
		    e.preventDefault();
		    $($(this).data('target')).toggleClass('hidden');
		    if( $(this).text() == 'Show Line Variation' ) {
			$(this).text('Hide Line Variation');
		    } else {
			$(this).text('Show Line Variation');
		    }
		});

	    /**
	     * Widgets for the collation form interface
	     *
	     */
	    /*
	    var listGroup = document.getElementById('poem-table-body');
	    Sortable.create(listGroup, {
		handle: '.glyphicon-move'
	    });
	    */

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

	    /*
		    ajax: {
			url: "search/poems",
			dataType: 'json',
			delay: 250,
			processResults: function (data, params) {
			    // parse the results into the format expected by Select2
			    // since we are using custom formatting functions we do not need to
			    // alter the remote JSON data, except to indicate that infinite
			    // scrolling can be used

			    params.page = params.page || 1;

			    return {
				results: data.items,
				pagination: {
				    more: (params.page * 30) < data.total_count
				}
			    };
			},
			cache: false
		    },
		    escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
		    minimumInputLength: 1,
		    templateResult: formatData, // omitted for brevity, see the source of this page
		    templateSelection: formatDataSelection // omitted for brevity, see the source of this page
	     */

	    /**
	     *
	     */

	    /*
	    $.get('search/poems', function(response) {
		    
		    var data = JSON.parse(response);

		    $.each(data.items, function(i, e) {
			    $("#poems-select2").append('<option value="' + e + '">' + e + '</option>');
			});
		});

	    $("#poems-select2").select2({
		    placeholder: "Select a Poem",
			allowClear: true,
			}).on("change", function(event) {

				var slug = $(event.target).val();
				// Work-around due to the directory structure
				slug = slug.replace(/\-$/, '');

				// Redirect the user to the appropriate Poem
				window.location.assign('poems/' + slug);
			    });
	    */
	});
}(jQuery));
