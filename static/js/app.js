/**
 * AngularJS integration
 *
 */

'use strict';

//angular.module('swiftCollate', ['ngSanitize', 'ngWebSocket', 'ui.select'])
angular.module('swiftCollate', ['ngSanitize', 'ngWebSocket'])
    .factory('Stream', function($websocket, $rootScope, $q) {
	    // Open a WebSocket connection
	    var dataStream = $websocket('ws://santorini0.stage.lafayette.edu/collate/stream');
	    //var dataStream = $websocket('wss://santorini0.stage.lafayette.edu/collate/stream');

	    var data = "<span>No texts selected for collation</span>";

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
	    /*
	    Stream.listen().then(function(message) {
		    $scope.Stream.data = message.data;
		    $scope.status = $sce.trustAsHtml($scope.Stream.data);
		});
	    */
	})
    .controller('FormController', function ($scope, Stream) {

	    /**
	     * To be integrated
	     *
	     */
	    $scope.poem = null;
	    $scope.baseText = {};
	    $scope.variants = {};
	    
	    $scope.requestCollation = function(event) {
		event.preventDefault();

		var params = { poem: $scope.poem, baseText: $scope.baseText, variants: $scope.variants };
		Stream.send(params);
	    };
	});
