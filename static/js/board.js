$(document).ready(function(){
    	elements = document.getElementsByClassName('image');
	for (var i = 0; i < elements.length; i++) {
		$.notify(size(elements[i]),'info');
	}
	function ajax_post() {
		$.ajax({
			url:"/"+board+"/post",
			type:"POST",
			data: new FormData($("#post-form")[0]),
			processData: false,
			contentType: false,
			enctype: "multipart/form-data",
			success:function(response){
				if (response.error){
					$.notify(response.type,'warn');
				}
				else {
					$.notify('Post enqueued','info');
				}
			},
			error:function(error){
				$.notify('Unknow Error','error');
			}
		});
	}

	var uploading = false;

	$("#post-form").submit(function(event){
		if (!uploading) {
			uploading = true;
			event.preventDefault();
			ajax_post();
			document.forms["post-form"].reset();
			uploading = false;
		} else {
			$.notify("Already uploading","warn");
		}
	});

	var socket = io.connect('http://' + document.domain + ':' + location.port + '/boarding');

	socket.on('newPost',function(post){
		if (post.status){
			if (sha_id == post.data.ip){
				$.notify('Post uploaded3','success');
			}
			else {
				$.notify('New post:'+post.data._id,'info');
			}
		}
		else {
			if (sha_id == post.data.ip){
				$.notify('Post not uploaded','error');
			}
		}
	});

});
