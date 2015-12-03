
/**
 * Widgets for the collation viewing interface
 *
 */

/**
 * Widgets for the collation form interface
 *
 */

(function($) {

    $(document).ready(function(e) {

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
	     * Set the default form state based upon cached values
	     *
	     */
	    if( $('.input-variant:checked').length > 0 ) {
		$('#input-variant-all').val('Deselect Transcripts');
	    }

	    if( $('.input-base-text:checked').length > 0 ) {
		$('#input-submit-collate').prop('disabled', false);
	    }

	    $('#input-base-text-reset').click(function(e) {
		    $('.input-base-text:checked').parents('tr').find('.input-variant').prop('disabled', false);
		    $('.input-base-text:checked').prop('checked', false);
		    $('.input-base-text').prop('disabled', false);
		    $('#input-submit-collate').prop('disabled', true);
		});

	    /**
	     * Handler for selecting the checkboxes for the base texts
	     *
	     */
	    $('.input-base-text').change(function(e) {
		    if( $(this).prop('checked') ) {

			// Disable the other elements
			$('.input-base-text').filter(function(i,e) { return !$(e).is('.input-base-text:checked:first'); } ).prop('disabled', true);
			$('#input-submit-collate').prop('disabled', false);

			$(this).parents('tr').find('.input-variant').prop('checked', false);
			$(this).parents('tr').find('.input-variant').prop('disabled', true);
		    } else {
			$('.input-base-text').prop('disabled', false);
			$('.input-base-text').prop('checked', false);
			$('#input-submit-collate').prop('disabled', true);

			$(this).parents('tr').find('.input-variant').prop('disabled', false);
		    }
		});

	    $('#input-variant-all').click(function(e) {
					      if( $('.input-variant:checked').length > 0 ) {
						  $('.input-variant:checked').prop('checked', false);
						  $(this).val('Select All Transcripts');
					      } else {
						  $('.input-variant').prop('checked', true);
						  $(this).val('Deselect Transcripts');
					      }
					  });


	    /**
	     * Handler for selecting the checkboxes for the variants
	     *
	     */
	    $('.input-variant').click(function(e) {
		    if( $(this).prop('checked') && $('.input-variant:checked').length == 1) {
			$('#input-variant-all').val('Deselect Transcripts');
			//$('#input-submit-collate').prop('disabled', false);
		    } else if(!$(this).prop('checked') && $('.input-variant:checked').length == 0) {
			$('#input-variant-all').val('Select All Transcripts');
			//$('#input-submit-collate').prop('disabled', true);
		    }
		});

	});
}(jQuery));
