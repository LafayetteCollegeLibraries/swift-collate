/**
 * AngularJS integration
 *
 */

'use strict';

//angular.module('swiftCollate', ['ngSanitize', 'ngWebSocket', 'ui.select'])
angular.module('swiftCollate', ['ngSanitize', 'ngWebSocket'])
    .factory('Stream', function($websocket, $rootScope, $q) {

	    // Open a WebSocket connection
	    var dataStream = $websocket('wss://' + window.location.hostname + '/stream');
	    var data = "";

	    /*
	    var methods = {
		'data': data,
		listen: function() {
		    var deferred = $q.defer();

		    dataStream.onMessage(function(message) {
			    $rootScope.$apply( function() {
				    deferred.resolve(message);
				});
			});

		    return deferred.promise;
		}
	    };
	    */

	    /**
	     * Work-around for submitting requests to begin a collation
	     *
	     */
	    /*
	    $("#collate-form").submit(function(event) {
		    event.preventDefault();
		    
		    var transmitStream = new WebSocket('ws://santorini0.stage.lafayette.edu/collate/stream');
		    transmitStream.send( $(this).serializeArray() );
		});
	    */

	    var methods = {
		'data': data,
		listen: function(callback) {
		    dataStream.onMessage(function(message) {
			    $rootScope.$apply( function() {
				    callback.call(this, message);
				    //console.log(message);
				});
			})
		},
		send: function(message) {
		    dataStream.send( JSON.stringify(message) );
		}
	    };

	    return methods;
	})
    .controller('StreamController', function ($scope, Stream, $compile, $sce) {
	    $scope.Stream = Stream;
	    $scope.status = $sce.trustAsHtml($scope.Stream.data);
	    $scope.resetCollation = function(event) {
		$("#collation-content").empty();
	    };

	    Stream.listen(function(message) {
		    $scope.Stream.data = message.data;
		    $scope.status = $sce.trustAsHtml($scope.Stream.data);
		});
	    // @todo Refactor using a Promise instance
	    /*
	    Stream.listen().then(function(message) {
		    $scope.Stream.data = message.data;
		    $scope.status = $sce.trustAsHtml($scope.Stream.data);
		});
	    */

	    // @todo Deduplicate
	    $scope.requestCollation = function(event) {
		event.preventDefault();

		var params = { poem: $scope.poem,
			       baseText: $scope.baseText,
			       variants: $scope.variants,
			       tokenizer: $scope.tokenizer,
			       tagger: $scope.tagger };

		/*
		// Work-around
		var variants = $scope.variants;
		if( !$('#variant-fields').hasClass('in') ) {
		    variants = $scope.allVariants;
		}

		var params = { poem: $scope.poem,
			       baseText: $scope.baseText,
			       variants: variants,
			       tokenizer: $scope.tokenizer };
		*/

		Stream.send(params);
	    };
	})
    .controller('TranscriptController', function ($scope) {
	    $('[data-toggle="popover"]').popover();
	})
    .controller('FormController', function ($scope, Stream) {

	    /**
	     * To be integrated
	     *
	     */
	    $scope.poem = null;
	    //$scope.baseText = null; // Select the first arbitrary value
	    // Work-around to set the widget to the default value
	    //$scope.baseText = $('#base-text-select2 option[selected="selected"]').val();
	    $scope.baseText = {};
	    $scope.variants = {};

	    // By default, the variants should be populated
	    // @todo Populate this from a server endpoint
	    var variants = {};
	    $('input[type="checkbox"][name="variants"]:checked').each(function(i) {
		    variants[$(this).val()] = $(this).val();
		    //$(this).prop('checked', true);
		});

	    //$scope.allVariants = variants;
	    $scope.variants = variants;

	    // Work-arounds
	    $scope.mode = 'notaBene';
	    $scope.tokenizer = 'SwiftSentenceTokenizer';
	    $scope.tagger = 'disabled';
	    
	    $scope.requestCollation = function(event) {
		event.preventDefault();

		var params = { poem: $scope.poem,
			       baseText: $scope.baseText,
			       variants: $scope.variants,
			       mode: $scope.mode,
			       tokenizer: $scope.tokenizer,
			       tagger: $scope.tagger };
		/*
		// Work-around
		var variants = $scope.variants;
		if( !$('#variant-fields').hasClass('in') ) {
		    variants = $scope.allVariants;
		}

		var params = { poem: $scope.poem,
			       baseText: $scope.baseText,
			       variants: variants,
			       tokenizer: $scope.tokenizer };
		*/
		Stream.send(params);
	    };
	    // @todo Deduplicate
	    $scope.resetCollation = function(event) {
		$("#collation-content").empty();
	    };
	})
    .controller('SearchController', function($scope) {

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

	    var pathname = window.location.pathname;

	    $.get('/suggest/poems', function(response) {
		    
		    var data = JSON.parse(response);

		    $.each(data.items, function(i, e) {
			    $("#poems-select2").append('<option value="' + e + '">' + e + '</option>');
			});
		});

	    $("#poems-select2").select2({
		    placeholder: "Browse by Poem ID",
		    allowClear: true,
	    }).on("select2:select", function(event) {
		    var slug = $(event.target).val();

		    // Redirect the user to the appropriate Poem
		    window.location.assign('/poems/' + slug);
		});
	});
