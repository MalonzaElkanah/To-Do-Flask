/*
Author       : Malone
Template Name: Elkanah - to_do/index.html
Version      : 1.0
*/

(function($) {
    "use strict";

    $(".add-list").on('click', function () {
    	var num = parseInt($("input[name='list_num']").val());
    	num = num + 1;
    	$("input[name='list_num']").val(''+num+'');

        var editcontent = '<li class="list-group-item d-flex justify-content-between align-items-center">' +
			'<div class="col-10">' +
				'<div class="form-group">' +
					'<input type="text" class="form-control"  name="list'+num+'" placeholder="New List Item">' +
				'</div>' +
			'</div>' +
			'<div class="col-2">' +
				'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i>Remove</a>' +
			'</div>' +
		'</li>';
		
        $(".new-list-group").append(editcontent);
        $("#add-list-btn").show();
        return false;
    });

	// Edit List Add More
    $(".editList-info").on('click','.trash', function () {
		$(this).closest('.edit-cont').remove();
		return false;
    });

	
})(jQuery);
